from typing import Optional, TYPE_CHECKING

from src.utils.config import get_config
from src.services.permission_service import permission_service
from src.services.discord_guard_service import discord_guard_service
from src.services.input_guard_service import input_guard_service
from src.services.abuse_guard_service import abuse_guard_service
from src.services.api_guard_service import api_guard_service
from src.services.secret_guard_service import secret_guard_service
from src.services.file_guard_service import file_guard_service
from src.services.audit_service import audit_service

if TYPE_CHECKING:
    import discord


class SecurityHardeningService:
    def __init__(self):
        self.config = get_config()
        self.enabled = getattr(self.config, 'SECURITY_ENABLED', True)
        
    async def check_permission(
        self,
        interaction,
        command_name: str,
        admin_role_id: Optional[str] = None
    ) -> tuple[bool, str]:
        if not self.enabled:
            return True, "Security disabled"
        
        return await permission_service.check_command_permission(
            interaction, command_name, admin_role_id
        )
    
    def check_message_safety(self, message) -> tuple[bool, str]:
        if not self.enabled:
            return True, "Security disabled"
        
        return discord_guard_service.is_safe_message(message)
    
    def validate_player_id(self, player_id: str) -> tuple[bool, str]:
        if not self.enabled:
            return True, player_id
        
        return input_guard_service.validate_player_id(player_id)
    
    def validate_gift_code(self, code: str) -> tuple[bool, str]:
        if not self.enabled:
            return True, code
        
        return input_guard_service.validate_gift_code(code)
    
    def check_abuse(self, guild_id: str, user_id: str, action: str) -> tuple[bool, str]:
        if not self.enabled:
            return True, "OK"
        
        if action == "register":
            return abuse_guard_service.check_register_rate_limit(guild_id, user_id)
        elif action == "redeem":
            return abuse_guard_service.check_redeem_rate_limit(guild_id, user_id)
        elif action == "setup":
            return abuse_guard_service.check_setup_rate_limit(guild_id, user_id)
        
        return True, "OK"
    
    async def record_invalid_input(self, guild_id: str, user_id: str, input_type: str, sample: str):
        if self.enabled:
            await abuse_guard_service.record_invalid_input(guild_id, user_id, input_type, sample)
    
    def is_user_blocked(self, guild_id: str, user_id: str) -> bool:
        if not self.enabled:
            return False
        
        return abuse_guard_service.is_user_blocked(guild_id, user_id)
    
    def sanitize_for_embed(self, text: str) -> str:
        return discord_guard_service.sanitize_for_embed(text)
    
    def get_allowed_mentions(self):
        return discord_guard_service.get_allowed_mentions()
    
    def redact_for_log(self, text: str) -> str:
        return secret_guard_service.redact_for_log(text)
    
    def check_backup_security(self, backup_path) -> tuple[bool, list]:
        if not self.enabled:
            return True, []
        
        return file_guard_service.scan_backup_directory(backup_path)
    
    def verify_backup_integrity(self, backup_path) -> tuple[bool, str]:
        return file_guard_service.verify_backup_integrity(backup_path)
    
    def delete_unsafe_backup(self, backup_path) -> bool:
        return file_guard_service.delete_unsafe_backup(backup_path)
    
    def log_admin_action(
        self,
        guild_id: str,
        actor_id: str,
        command: str,
        success: bool,
        reason: str = None
    ):
        audit_service.log_admin_command(guild_id, actor_id, command, success, reason)
    
    def log_security_event(
        self,
        guild_id: str,
        actor_id: str,
        event_type: str,
        severity: str,
        details: str = None
    ):
        audit_service.log_security_event(guild_id, actor_id, event_type, severity, details)


security_hardening_service = SecurityHardeningService()
