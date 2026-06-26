from typing import Optional, TYPE_CHECKING

from database import save_audit_log, save_security_incident
from src.utils.config import get_config
from src.utils.permissions import SENSITIVE_COMMANDS, check_admin_role
from src.services.alert_service import alert_service

if TYPE_CHECKING:
    import discord


class PermissionService:
    def __init__(self):
        self.config = get_config()
        self._denied_attempts: dict[str, int] = {}
        
    async def check_command_permission(
        self,
        interaction,
        command_name: str,
        admin_role_id: Optional[str] = None
    ) -> tuple[bool, str]:
        guild = getattr(interaction, 'guild', None)
        user = getattr(interaction, 'user', None)
        
        if not guild:
            return True, "DM"
        
        if not user:
            return False, "No user"
        
        if command_name not in SENSITIVE_COMMANDS:
            return True, "Non-sensitive command"
        
        perms = getattr(user, 'guild_permissions', None)
        if perms and getattr(perms, 'administrator', False):
            return True, "Administrator"
        
        if admin_role_id and await self._check_admin_role(interaction, admin_role_id):
            return True, "Admin role"
        
        user_id = str(user.id)
        guild_id = str(guild.id)
        key = f"{guild_id}:{user_id}"
        
        self._denied_attempts[key] = self._denied_attempts.get(key, 0) + 1
        
        await self._handle_denied_attempt(
            guild,
            user,
            command_name,
            guild_id
        )
        
        return False, "Permission denied"
    
    async def _check_admin_role(self, interaction, role_id: str) -> bool:
        return check_admin_role(interaction, role_id)
    
    async def _handle_denied_attempt(
        self,
        guild,
        user,
        command_name: str,
        guild_id: str
    ):
        user_id = str(user.id)
        key = f"{guild_id}:{user_id}"
        
        save_audit_log(
            guild_id=guild_id,
            actor_id=user_id,
            action=f"COMMAND_DENIED:{command_name}",
            target=command_name,
            result="DENIED",
            risk_level="WARNING",
            metadata=f"User attempted to use {command_name}"
        )
        
        if self._denied_attempts.get(key, 0) >= 3:
            save_security_incident(
                guild_id=guild_id,
                incident_type="ADMIN_COMMAND_ABUSE",
                severity="WARNING",
                message=f"User {user_id} denied {self._denied_attempts[key]} admin commands",
                action_taken="Logged"
            )
            
            await alert_service.send_security_alert(
                f"Admin command abuse from {user_id}",
                f"User attempted {self._denied_attempts[key]} denied admin commands"
            )
    
    def reset_denied_attempts(self, guild_id: str, user_id: str):
        key = f"{guild_id}:{user_id}"
        if key in self._denied_attempts:
            del self._denied_attempts[key]
    
    def get_denied_count(self, guild_id: str, user_id: str) -> int:
        key = f"{guild_id}:{user_id}"
        return self._denied_attempts.get(key, 0)


permission_service = PermissionService()
