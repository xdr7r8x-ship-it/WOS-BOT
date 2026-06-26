import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestPermissionService:
    def test_permission_service_import(self):
        from src.services.permission_service import permission_service
        assert permission_service is not None
    
    def test_permission_service_has_methods(self):
        from src.services.permission_service import permission_service
        assert hasattr(permission_service, 'check_command_permission')
        assert hasattr(permission_service, 'reset_denied_attempts')
        assert hasattr(permission_service, 'get_denied_count')
    
    def test_sensitive_commands(self):
        from src.utils.permissions import SENSITIVE_COMMANDS
        assert "setup" in SENSITIVE_COMMANDS
        assert "backup_create" in SENSITIVE_COMMANDS
        assert "rollback" in SENSITIVE_COMMANDS
        assert "updates_apply" in SENSITIVE_COMMANDS
    
    def test_is_admin_command(self):
        from src.utils.permissions import is_admin_command
        assert is_admin_command("setup") is True
        assert is_admin_command("backup_create") is True
        assert is_admin_command("redeem") is False
        assert is_admin_command("status") is False
