#pragma once

#include "src/pch.hpp"
#include "src/Utils/VTableHookBase.hpp"

// ATgPawn::TGPostRenderFor — native invoked per pawn during HUD render.
// Signature: TGPostRenderFor(APlayerController* PC, UCanvas* Canvas,
// FVector CameraPosition, FVector CameraDir). Stack args total 32 bytes
// (PC* + Canvas* + 3*float + 3*float). Thiscall: this in ECX.
// We log the pawn + count at +0xFFC to see whether bots get iterated.
//
// Only ever reached via virtual dispatch through vtable+0x498 (confirmed live
// 2026-07-31 via a Ghidra debugger memory read of the CDO's vtable) — the
// UC "exec" bytecode-unmarshal stub at 0x1097eef0 forwards here but decodes
// params from the FFrame bytecode stream rather than a fixed Parms struct, so
// it isn't a viable hook point the way a normal native is. Hooked via
// VTableHookBase against ATgPawn_Character specifically (not the base
// ATgPawn) because real player/bot pawns are always ATgPawn_Character
// instances, which have their OWN vtable distinct from ATgPawn's, even though
// neither overrides this particular slot (both currently resolve to the same
// implementation address).
class TgPawn__TGPostRenderFor : public VTableHookBase<
	void(__fastcall*)(ATgPawn*, void*, void*, void*, float, float, float, float, float, float),
	ATgPawn_Character,
	0x498,
	TgPawn__TGPostRenderFor> {
public:
	static void __fastcall Call(ATgPawn* Pawn, void* edx, void* PC, void* Canvas,
		float cpX, float cpY, float cpZ, float cdX, float cdY, float cdZ);
	static inline void __fastcall CallOriginal(ATgPawn* Pawn, void* edx, void* PC, void* Canvas,
		float cpX, float cpY, float cpZ, float cdX, float cdY, float cdZ) {
		m_original(Pawn, edx, PC, Canvas, cpX, cpY, cpZ, cdX, cdY, cdZ);
	}
};
