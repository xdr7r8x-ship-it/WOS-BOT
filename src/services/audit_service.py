from typing import Optional

from database import save_audit_log
from src.utils.redaction import redact_dict, redact_text


AUDITABLE_ACTIONS = {
    "ADMIN_COMMAND_EXECUTED",
    "ADMIN_COMMAND_DENIED",
    "BACKUP_CREATED",
    "BACKUP_RESTORED",
    "UPDATE_CHECKED",
    "UPDATE_APPLIED",
    "UPDATE_FAILED",
    "SECURITY_SCAN_RUN",
    "DIAGNOSTICS_RUN",
    "SETUP_CHANGED",
    "PLAYER_REMOVED",
    "PLAYER_DISABLED",
    "CLEANUP_RUN",
    "RETRY_RUN",
    "LOGIN_ATTEMPT",
    "PERMISSION_DENIED",
}


RISK_LEVELS = {
    "LOW": ["ADMIN_COMMAND_EXECUTED", "DIAGNOSTICS_RUN"],
    "MEDIUM": ["SETUP_CHANGED", "PLAYER_REMOVED", "CLEANUP_RUN", "RETRY_RUN"],
    "HIGH": ["BACKUP_CREATED", "BACKUP_RESTORED", "UPDATE_APPLIED"],
    "WARNING": ["ADMIN_COMMAND_DENIED", "PERMISSION_DENIED", "UPDATE_FAILED"],
    "CRITICAL": ["LOGIN_ATTEMPT"],
}


class AuditService:
    def __init__(self):
        pass
    
    def log_action(
        self,
        guild_id: str,
        actor_id: str,
        action: str,
        target: str = None,
        result: str = "SUCCESS",
        metadata: dict = None
    ) -> None:
        risk_level = self._get_risk_level(action)
        
        sanitized_metadata = None
        if metadata:
            sanitized_metadata = str(redact_dict(metadata))
        
        safe_target = redact_text(str(target)) if target else None
        
        save_audit_log(
            guild_id=guild_id,
            actor_id=actor_id,
            action=action,
            target=safe_target,
            result=result,
            risk_level=risk_level,
            metadata=sanitized_metadata
        )
    
    def _get_risk_level(self, action: str) -> str:
        for level, actions in RISK_LEVELS.items():
            if action in actions:
                return level
        return "INFO"
    
    def log_admin_command(
        self,
        guild_id: str,
        actor_id: str,
        command: str,
        success: bool,
        reason: str = None
    ):
        action = "ADMIN_COMMAND_EXECUTED" if success else "ADMIN_COMMAND_DENIED"
        
        self.log_action(
            guild_id=guild_id,
            actor_id=actor_id,
            action=action,
            target=command,
            result="SUCCESS" if success else "DENIED",
            metadata={"reason": reason} if reason else None
        )
    
    def log_backup(
        self,
        guild_id: str,
        actor_id: str,
        backup_name: str,
        success: bool,
        size_bytes: int = None
    ):
        action = "BACKUP_CREATED" if success else "BACKUP_FAILED"
        
        self.log_action(
            guild_id=guild_id,
            actor_id=actor_id,
            action=action,
            target=backup_name,
            result="SUCCESS" if success else "FAILED",
            metadata={"size_bytes": size_bytes} if size_bytes else None
        )
    
    def log_update(
        self,
        guild_id: str,
        actor_id: str,
        from_version: str,
        to_version: str,
        success: bool
    ):
        action = "UPDATE_APPLIED" if success else "UPDATE_FAILED"
        
        self.log_action(
            guild_id=guild_id,
            actor_id=actor_id,
            action=action,
            target=f"{from_version} -> {to_version}",
            result="SUCCESS" if success else "FAILED"
        )
    
    def log_security_event(
        self,
        guild_id: str,
        actor_id: str,
        event_type: str,
        severity: str,
        details: str = None
    ):
        action = f"SECURITY_{event_type}"
        
        self.log_action(
            guild_id=guild_id,
            actor_id=actor_id,
            action=action,
            result=severity,
            metadata={"details": details} if details else None
        )
    
    def is_auditable_action(self, action: str) -> bool:
        return action in AUDITABLE_ACTIONS


audit_service = AuditService()
