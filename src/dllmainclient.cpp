#include "src/pch.hpp"

#include "src/Utils/DebugWindow/DebugWindow.hpp"
#include "src/GameServer/Core/UObject/ProcessEvent/UObject__ProcessEvent.hpp"
#include "src/GameServer/TgGame/TgDeployable/NotifyGroupChanged/TgDeployable__NotifyGroupChanged.hpp"
#include "src/GameServer/TgGame/TgRepInfo_Game/GetTaskForceFor/TgRepInfo_Game__GetTaskForceFor.hpp"
#include "src/GameServer/TgGame/TgDeployable/IsFriendlyWithLocalPawn/TgDeployable__IsFriendlyWithLocalPawn.hpp"
#include "src/GameServer/TgGame/TgPawn/TGPostRenderFor/TgPawn__TGPostRenderFor.hpp"
#include "src/GameServer/TgGame/TgHUD_Game/DrawActorOverlays/TgHUD_Game__DrawActorOverlays.hpp"

unsigned long ModuleThread( void* ) {
	// Logger::LogDir defaults to "C:" (see Logger.hpp) -- historically fine
	// under Wine, where "C:" is the prefix's own writable drive_c sandbox.
	// Running natively on Windows, that's the real drive root, which a
	// normal (non-elevated) process -- and unreliably even an elevated one,
	// depending on how it was launched -- cannot write to; channel writes
	// were silently failing with no error (2026-07-31 investigation). Point
	// at the system temp dir instead, which any process can always write to.
	{
		char tempPath[MAX_PATH] = {};
		DWORD len = ::GetTempPathA(MAX_PATH, tempPath);
		if (len > 0 && len < MAX_PATH) {
			if (tempPath[len - 1] == '\\') tempPath[len - 1] = '\0';  // LogDir: no trailing slash
			Logger::LogDir = tempPath;
		}
	}

	::DetourTransactionBegin();
	::DetourUpdateThread(::GetCurrentThread());
	Logger::EnableChannel("stealth");
	Logger::EnableChannel("hook_calltree");
	Logger::EnableChannel("replicated_event");
	Logger::EnableChannel("heal_tick");
	Logger::EnableChannel("team_colors");
	Logger::EnableChannel("damage-info");
	Logger::EnableChannel("nameplate");

	UObject__ProcessEvent::Install();
	TgDeployable__NotifyGroupChanged::Install();
	// Client-side DIAGNOSTICS (not a real fix) — route deployable friendship
	// checks through the Instigator chain when the DRI path is unusable.
	// See each hook's hpp for why this isn't the solution; DRI replication
	// itself still needs to be repaired on the server side.
	TgRepInfo_Game__GetTaskForceFor::Install();        // DRI non-null but fields null
	TgDeployable__IsFriendlyWithLocalPawn::Install();  // r_DRI null entirely (medstation)
	// Nameplate investigation -- diagnostic-only, logs on the "nameplate" channel.
	TgPawn__TGPostRenderFor::Install();
	TgHUD_Game__DrawActorOverlays::Install();

	::DetourTransactionCommit();
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpReserved)
{
	switch (fdwReason)
	{
		case DLL_PROCESS_ATTACH:
            DisableThreadLibraryCalls(hinstDLL);
			CreateThread( 0, 0, reinterpret_cast<LPTHREAD_START_ROUTINE>(ModuleThread), 0, 0, 0 );

			DebugWindow::WindowTitle = "CLIENT";
			CreateThread( 0, 0, reinterpret_cast<LPTHREAD_START_ROUTINE>(DebugWindow::ModuleThread), 0, 0, 0 );
			break;
		case DLL_THREAD_ATTACH:
			break;
		case DLL_THREAD_DETACH:
			break;
		case DLL_PROCESS_DETACH:
			break;
	}
	return TRUE;
}
