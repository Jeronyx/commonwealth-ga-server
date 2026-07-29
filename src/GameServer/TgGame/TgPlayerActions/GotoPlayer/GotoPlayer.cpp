#include "src/GameServer/TgGame/TgPlayerActions/GotoPlayer/GotoPlayer.hpp"

#include "src/GameServer/Storage/ClientConnectionsData/ClientConnectionsData.hpp"
#include "src/Utils/Logger/Logger.hpp"

namespace TgPlayerActions::GotoPlayerCmd {

namespace {

ATgPlayerController* FindControllerBySessionGuid(const std::string& guid) {
	for (auto& kv : GClientConnectionsData) {
		if (kv.second.SessionGuid == guid) return kv.second.Controller;
	}
	return nullptr;
}

ATgPawn_Character* FindPawnBySessionGuid(const std::string& guid) {
	for (auto& kv : GClientConnectionsData) {
		if (kv.second.SessionGuid == guid) return kv.second.Pawn;
	}
	return nullptr;
}

// Modest lift above the target's own Location so the spectator's camera
// lands near their head rather than inside their collision mesh.
constexpr float kViewOffsetZ = 150.0f;

} // namespace

void Execute(const std::string& acting_session_guid, const std::string& target_session_guid) {
	ATgPlayerController* pc = FindControllerBySessionGuid(acting_session_guid);
	if (!pc) {
		Logger::Log("chat-command", "goto_player guid=%s: no live controller\n",
			acting_session_guid.c_str());
		return;
	}

	ATgPawn_Character* target = FindPawnBySessionGuid(target_session_guid);
	if (!target) {
		Logger::Log("chat-command", "goto_player guid=%s: target guid=%s has no live pawn\n",
			acting_session_guid.c_str(), target_session_guid.c_str());
		return;
	}

	FVector dest = target->Location;
	dest.Z += kViewOffsetZ;
	pc->ClientSetLocation(dest, pc->Rotation);

	Logger::Log("chat-command", "goto_player guid=%s: moved to target guid=%s loc=(%.0f,%.0f,%.0f)\n",
		acting_session_guid.c_str(), target_session_guid.c_str(), dest.X, dest.Y, dest.Z);
}

} // namespace TgPlayerActions::GotoPlayerCmd
