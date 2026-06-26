from datetime import datetime
from typing import Optional

from database import (
    check_command_rate_limit,
    block_input,
    is_input_blocked,
    get_blocked_user_count,
    save_audit_log,
    save_security_incident
)
from src.utils.config import get_config
from src.utils.security import hash_input
from src.services.alert_service import alert_service


class AbuseGuardService:
    def __init__(self):
        self.config = get_config()
        self._temp_blocks: dict[str, datetime] = {}
        self._register_attempts: dict[str, list[datetime]] = {}
        self._redeem_attempts: dict[str, list[datetime]] = {}
        
        self.max_invalid_inputs = getattr(self.config, 'MAX_INVALID_INPUTS_PER_WINDOW', 5)
        self.abuse_window = getattr(self.config, 'ABUSE_WINDOW_SECONDS', 120)
        self.temp_block_seconds = getattr(self.config, 'TEMP_BLOCK_SECONDS', 600)
        self.admin_deny_alert_threshold = getattr(self.config, 'ADMIN_DENIED_ALERT_THRESHOLD', 3)
        
    def check_register_rate_limit(self, guild_id: str, user_id: str) -> tuple[bool, str]:
        key = f"{guild_id}:{user_id}"
        now = datetime.utcnow()
        
        if key in self._temp_blocks:
            if (now - self._temp_blocks[key]).total_seconds() < self.temp_block_seconds:
                return False, "TEMPORARILY_BLOCKED"
        
        if key not in self._register_attempts:
            self._register_attempts[key] = []
        
        self._register_attempts[key] = [
            t for t in self._register_attempts[key]
            if (now - t).total_seconds() < self.abuse_window
        ]
        
        self._register_attempts[key].append(now)
        
        if len(self._register_attempts[key]) > self.max_invalid_inputs:
            self._temp_blocks[key] = now
            save_security_incident(
                guild_id=guild_id,
                incident_type="REGISTER_ABUSE",
                severity="WARNING",
                message=f"User {user_id} exceeded invalid registration limit",
                action_taken="Temporary block"
            )
            return False, "TEMPORARILY_BLOCKED"
        
        return True, "OK"
    
    def check_redeem_rate_limit(self, guild_id: str, user_id: str) -> tuple[bool, str]:
        allowed, count = check_command_rate_limit(
            guild_id, user_id, "redeem", max_count=5, window_seconds=300
        )
        
        if not allowed:
            save_audit_log(
                guild_id=guild_id,
                actor_id=user_id,
                action="REDEEM_RATE_LIMITED",
                target="",
                result="BLOCKED",
                risk_level="INFO"
            )
        
        return allowed, "RATE_LIMITED" if not allowed else "OK"
    
    def check_setup_rate_limit(self, guild_id: str, user_id: str) -> tuple[bool, str]:
        allowed, count = check_command_rate_limit(
            guild_id, user_id, "setup", max_count=3, window_seconds=300
        )
        
        if not allowed:
            save_security_incident(
                guild_id=guild_id,
                incident_type="SETUP_SPAM",
                severity="WARNING",
                message=f"User {user_id} spam attempting setup",
                action_taken="Rate limited"
            )
        
        return allowed, "RATE_LIMITED" if not allowed else "OK"
    
    async def record_invalid_input(self, guild_id: str, user_id: str, input_type: str, sample: str):
        sample_hash = hash_input(sample)
        
        if is_input_blocked(guild_id, user_id, sample_hash):
            return
        
        block_input(
            guild_id=guild_id,
            user_id=user_id,
            input_type=input_type,
            reason="Invalid input pattern",
            sample_hash=sample_hash
        )
        
        block_count = get_blocked_user_count(guild_id, user_id)
        
        if block_count >= self.max_invalid_inputs:
            key = f"{guild_id}:{user_id}"
            self._temp_blocks[key] = datetime.utcnow()
            
            save_security_incident(
                guild_id=guild_id,
                incident_type="INPUT_ABUSE",
                severity="WARNING",
                message=f"User {user_id} blocked for excessive invalid inputs",
                action_taken="Temporary block"
            )
            
            await alert_service.send_security_alert(
                f"Input abuse detected from {user_id}",
                f"User blocked for {block_count} invalid inputs"
            )
    
    def is_user_blocked(self, guild_id: str, user_id: str) -> bool:
        key = f"{guild_id}:{user_id}"
        
        if key in self._temp_blocks:
            if (datetime.utcnow() - self._temp_blocks[key]).total_seconds() >= self.temp_block_seconds:
                del self._temp_blocks[key]
                return False
            return True
        
        return False
    
    def check_command_rate_limit_db(
        self,
        guild_id: str,
        user_id: str,
        command_name: str,
        max_count: int = 10,
        window_seconds: int = 60
    ) -> tuple[bool, int]:
        return check_command_rate_limit(guild_id, user_id, command_name, max_count, window_seconds)
    
    def cleanup_old_blocks(self):
        now = datetime.utcnow()
        expired = [
            k for k, v in self._temp_blocks.items()
            if (now - v).total_seconds() >= self.temp_block_seconds
        ]
        for k in expired:
            del self._temp_blocks[k]
        
        for key in list(self._register_attempts.keys()):
            self._register_attempts[key] = [
                t for t in self._register_attempts[key]
                if (now - t).total_seconds() < self.abuse_window
            ]
            if not self._register_attempts[key]:
                del self._register_attempts[key]


abuse_guard_service = AbuseGuardService()
