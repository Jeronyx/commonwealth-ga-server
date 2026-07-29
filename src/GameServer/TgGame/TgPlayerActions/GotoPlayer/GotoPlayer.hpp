#pragma once

#include <string>

namespace TgPlayerActions::GotoPlayerCmd {

// -nextplayer / -prevplayer: teleport the spectator's own camera to
// target_session_guid's current pawn location. acting_session_guid is the
// spectator (resolved via ClientConnectionData::Controller -- spectators
// have no Pawn to walk through, only a controller); target_session_guid is
// a real player (resolved via ClientConnectionData::Pawn, same as every
// other TgPlayerActions command). Silent no-op if either side can't be
// resolved (stale roster entry, disconnect mid-cycle, etc).
//
// Uses AController::ClientSetLocation -- the native UE3 RPC for a hard
// camera snap that overrides the client's own local movement prediction.
// This is NOT the same problem as SpectatorCameraSpeed: Location snaps via
// an explicit RPC rather than depending on property replication, so the
// "no push mechanism" issue that ruled out a speed increase doesn't apply
// here.
void Execute(const std::string& acting_session_guid, const std::string& target_session_guid);

}  // namespace TgPlayerActions::GotoPlayerCmd
