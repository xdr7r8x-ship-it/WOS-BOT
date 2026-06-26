from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import discord


SENSITIVE_COMMANDS = {
    "setup",
    "player_remove",
    "retry",
    "cleanup",
    "system",
    "diagnostics",
    "backup_create",
    "backup_list",
    "rollback",
    "updates_check",
    "updates_plan",
    "updates_apply",
    "watchdog_status",
    "security_scan",
    "integrity_check",
    "predict_status",
    "autopilot_status",
}


def is_admin_command(command_name: str) -> bool:
    return command_name in SENSITIVE_COMMANDS


def check_admin_role(interaction, role_id: str) -> bool:
    guild = getattr(interaction, 'guild', None)
    user = getattr(interaction, 'user', None)
    
    if not guild or not user:
        return False
    
    member = guild.get_member(user.id)
    if not member:
        return False
    
    for role in getattr(member, 'roles', []):
        if str(getattr(role, 'id', '')) == role_id:
            return True
    
    return False
