import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestSecretGuardService:
    def test_secret_guard_import(self):
        from src.services.secret_guard_service import secret_guard_service
        assert secret_guard_service is not None
    
    def test_secret_guard_has_methods(self):
        from src.services.secret_guard_service import secret_guard_service
        assert hasattr(secret_guard_service, 'scan_file_for_secrets')
        assert hasattr(secret_guard_service, 'check_backup_for_secrets')
        assert hasattr(secret_guard_service, 'redact_for_log')
    
    def test_scan_content_for_secrets_with_token(self):
        from src.services.secret_guard_service import secret_guard_service
        content = "DISCORD_BOT_TOKEN=secret123456789"
        result = secret_guard_service.scan_content_for_secrets(content)
        assert result is True
    
    def test_scan_content_for_secrets_without_token(self):
        from src.services.secret_guard_service import secret_guard_service
        content = "Just a normal message"
        result = secret_guard_service.scan_content_for_secrets(content)
        assert result is False
    
    def test_redact_for_log(self):
        from src.services.secret_guard_service import secret_guard_service
        text = "Token: ghp_abcdefghij1234567890klmnopqrstuvwx"
        result = secret_guard_service.redact_for_log(text)
        assert "ghp_" not in result
    
    def test_is_safe_to_backup_env(self):
        from src.services.secret_guard_service import secret_guard_service
        from pathlib import Path
        result = secret_guard_service.is_safe_to_backup(Path(".env"))
        assert result is False
    
    def test_is_safe_to_backup_normal_file(self):
        from src.services.secret_guard_service import secret_guard_service
        from pathlib import Path
        result = secret_guard_service.is_safe_to_backup(Path("main.py"))
        assert result is True
