from typing import Optional
from database import save_audit_log, get_guild_settings
from src.services.security_hardening_service import security_hardening_service
from src.services.permission_service import permission_service


async def check_admin_permission(interaction, command_name: str) -> tuple[bool, str]:
    guild_id = str(interaction.guild_id) if interaction.guild else "0"
    user_id = str(interaction.user.id) if interaction.user else "0"
    settings = get_guild_settings(guild_id)
    admin_role_id = settings.get("admin_role_id") if settings else None
    
    allowed, reason = await security_hardening_service.check_permission(
        interaction, command_name, admin_role_id
    )
    if not allowed:
        save_audit_log(
            guild_id, user_id, 
            f"AUTH_DENIED:{command_name}",
            command_name, "DENIED", "WARNING",
            f"Permission denied: {reason}"
        )
        return False, reason
    
    return True, "OK"


def check_abuse_guard(guild_id: str, user_id: str, action: str) -> tuple[bool, str]:
    allowed, reason = security_hardening_service.check_abuse(guild_id, user_id, action)
    return allowed, reason


def log_panel_action(
    guild_id: str,
    user_id: str,
    action: str,
    target: str = "",
    result: str = "SUCCESS",
    risk_level: str = "LOW",
    details: str = ""
):
    save_audit_log(
        guild_id=guild_id,
        actor_id=user_id,
        action=action,
        target=target,
        result=result,
        risk_level=risk_level,
        metadata=details
    )


def validate_player_id_input(player_id: str) -> tuple[bool, str]:
    valid, reason = security_hardening_service.validate_player_id(player_id)
    return valid, reason


def validate_gift_code_input(code: str) -> tuple[bool, str]:
    valid, reason = security_hardening_service.validate_gift_code(code)
    return valid, reason
