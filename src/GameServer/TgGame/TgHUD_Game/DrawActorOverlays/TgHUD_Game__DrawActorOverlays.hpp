#pragma once

#include "src/pch.hpp"
#include "src/Utils/VTableHookBase.hpp"

// ATgHUD_Game::DrawActorOverlays — the pawn iterator that per-actor dispatches
// TGPostRenderFor. If this doesn't fire, overhead rendering for ALL pawns is
// dead.
//
// Only ever reached via virtual dispatch through vtable+0x49c (confirmed live
// 2026-07-31 via a Ghidra debugger memory read of the CDO's vtable) — the UC
// "exec" bytecode-unmarshal stub forwards here but decodes params from the
// FFrame bytecode stream, not a viable hook point the way a normal native is.
// Hooked via VTableHookBase against ATgHUD_Game's own vtable.
class TgHUD_Game__DrawActorOverlays : public VTableHookBase<
	void(__fastcall*)(void*, void*),
	ATgHUD_Game,
	0x49c,
	TgHUD_Game__DrawActorOverlays> {
public:
	static void __fastcall Call(void* HUD, void* edx);
	static inline void __fastcall CallOriginal(void* HUD, void* edx) {
		m_original(HUD, edx);
	}
};
