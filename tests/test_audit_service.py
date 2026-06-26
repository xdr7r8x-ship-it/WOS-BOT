import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestAuditService:
    def test_audit_service_import(self):
        from src.services.audit_service import audit_service
        assert audit_service is not None
    
    def test_audit_service_has_methods(self):
        from src.services.audit_service import audit_service
        assert hasattr(audit_service, 'log_action')
        assert hasattr(audit_service, 'log_admin_command')
        assert hasattr(audit_service, 'log_backup')
    
    def test_is_auditable_action(self):
        from src.services.audit_service import audit_service
        assert audit_service.is_auditable_action("ADMIN_COMMAND_EXECUTED") is True
        assert audit_service.is_auditable_action("BACKUP_CREATED") is True
        assert audit_service.is_auditable_action("UNKNOWN_ACTION") is False
    
    def test_log_admin_command(self):
        from src.services.audit_service import audit_service
        audit_service.log_admin_command(
            guild_id="123",
            actor_id="456",
            command="setup",
            success=True
        )
    
    def test_log_backup(self):
        from src.services.audit_service import audit_service
        audit_service.log_backup(
            guild_id="123",
            actor_id="456",
            backup_name="backup_001",
            success=True,
            size_bytes=1024
        )
    
    def test_log_update(self):
        from src.services.audit_service import audit_service
        audit_service.log_update(
            guild_id="123",
            actor_id="456",
            from_version="1.0.0",
            to_version="1.1.0",
            success=True
        )
    
    def test_log_security_event(self):
        from src.services.audit_service import audit_service
        audit_service.log_security_event(
            guild_id="123",
            actor_id="456",
            event_type="SECRET_DETECTED",
            severity="CRITICAL",
            details="Token found in file"
        )
