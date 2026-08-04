#include "src/GameServer/TgGame/TgPawn/TGPostRenderFor/TgPawn__TGPostRenderFor.hpp"
#include "src/Utils/Logger/Logger.hpp"

// Rate-limit: avoid spamming log every frame for every pawn. Only log pawns
// that have pending damage-display entries (count > 0), and only once per
// (pawn, count) transition.
static int g_lastCount[256] = {0};
static void* g_lastPawn[256] = {0};
static int g_slotIdx = 0;

// Nameplate investigation (2026-08-01): does TGPostRenderFor even fire for
// visible pawns while spectating, and if it does, does the viewer's own PRI/
// Team look any different than a real player's? Separate channel/rate-limit
// from the damage-info diagnostic above -- a spectator idly watching has no
// damage-display entries to key off (count stays 0 forever), so that gate
// never fires for this investigation. Logged per (Pawn, PC) pair, once
// every ~2s, regardless of count.
static void* g_npLastPawn[64] = {0};
static void* g_npLastPC[64] = {0};
static DWORD g_npLastAt[64] = {0};
static int g_npSlot = 0;

void __fastcall TgPawn__TGPostRenderFor::Call(ATgPawn* Pawn, void* edx, void* PC, void* Canvas,
	float cpX, float cpY, float cpZ, float cdX, float cdY, float cdZ)
{
	if (Pawn) {
		int count = *(int*)((char*)Pawn + 0xFFC);
		unsigned flagsB4 = *(unsigned*)((char*)Pawn + 0xB4);
		unsigned flags3D8 = *(unsigned*)((char*)Pawn + 0x3D8);
		void* rOwner = *(void**)((char*)Pawn + 0x106C);

		// Only log when pawn has damage entries (what we care about)
		// and limit repeats: only log if pawn or count changed for that slot.
		if (count > 0) {
			bool seen = false;
			for (int i = 0; i < 256; i++) {
				if (g_lastPawn[i] == Pawn && g_lastCount[i] == count) { seen = true; break; }
			}
			if (!seen) {
				g_lastPawn[g_slotIdx] = Pawn;
				g_lastCount[g_slotIdx] = count;
				g_slotIdx = (g_slotIdx + 1) & 255;

				Logger::Log("damage-info",
					"TGPostRenderFor: pawn=%p count=%d flags+0xB4=0x%08x flags+0x3D8=0x%08x r_Owner=%p\n",
					Pawn, count, flagsB4, flags3D8, rOwner);
			}
		}

		if (Logger::IsChannelEnabled("nameplate") && PC) {
			const DWORD now = GetTickCount();
			bool seen = false;
			for (int i = 0; i < 64; i++) {
				if (g_npLastPawn[i] == Pawn && g_npLastPC[i] == PC && now - g_npLastAt[i] < 2000) { seen = true; break; }
			}
			if (!seen) {
				g_npLastPawn[g_npSlot] = Pawn;
				g_npLastPC[g_npSlot] = PC;
				g_npLastAt[g_npSlot] = now;
				g_npSlot = (g_npSlot + 1) & 63;

				ATgPlayerController* viewerPC = (ATgPlayerController*)PC;
				APlayerReplicationInfo* pawnPri = Pawn->PlayerReplicationInfo;
				APlayerReplicationInfo* viewerPri = viewerPC->PlayerReplicationInfo;
				void* pawnTeam = pawnPri ? (void*)pawnPri->Team : nullptr;
				void* viewerTeam = viewerPri ? (void*)viewerPri->Team : nullptr;

				Logger::Log("nameplate",
					"TGPostRenderFor FIRED: pawn=%p pawnPRI=%p pawnTeam=%p | viewerPC=%p viewerPawn=%p viewerPRI=%p viewerTeam=%p | sameTeamPtr=%d\n",
					Pawn, (void*)pawnPri, pawnTeam,
					PC, (void*)viewerPC->Pawn, (void*)viewerPri, viewerTeam,
					(pawnTeam && pawnTeam == viewerTeam) ? 1 : 0);
			}
		}
	}
	CallOriginal(Pawn, edx, PC, Canvas, cpX, cpY, cpZ, cdX, cdY, cdZ);
}
