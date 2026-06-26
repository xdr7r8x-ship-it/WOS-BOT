import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestSecurityHardeningService:
    def test_security_hardening_import(self):
        from src.services.security_hardening_service import security_hardening_service
        assert security_hardening_service is not None
    
    def test_security_hardening_has_methods(self):
        from src.services.security_hardening_service import security_hardening_service
        assert hasattr(security_hardening_service, 'check_permission')
        assert hasattr(security_hardening_service, 'validate_player_id')
        assert hasattr(security_hardening_service, 'check_abuse')
    
    def test_validate_player_id_valid(self):
        from src.services.security_hardening_service import security_hardening_service
        valid, result = security_hardening_service.validate_player_id("123456")
        assert valid is True
    
    def test_validate_player_id_invalid(self):
        from src.services.security_hardening_service import security_hardening_service
        valid, result = security_hardening_service.validate_player_id("abc")
        assert valid is False
    
    def test_validate_gift_code_valid(self):
        from src.services.security_hardening_service import security_hardening_service
        valid, result = security_hardening_service.validate_gift_code("ABC123")
        assert valid is True
    
    def test_validate_gift_code_invalid(self):
        from src.services.security_hardening_service import security_hardening_service
        valid, result = security_hardening_service.validate_gift_code("")
        assert valid is False
    
    def test_check_abuse_register(self):
        from src.services.security_hardening_service import security_hardening_service
        allowed, status = security_hardening_service.check_abuse("guild1", "user1", "register")
        assert allowed is True
        assert status == "OK"
    
    def test_sanitize_for_embed(self):
        from src.services.security_hardening_service import security_hardening_service
        result = security_hardening_service.sanitize_for_embed("Test @everyone")
        assert "@everyone" not in result
    
    def test_redact_for_log(self):
        from src.services.security_hardening_service import security_hardening_service
        text = "GitHub token: ghp_abcdefghij1234567890klmnopqrstuvwx"
        result = security_hardening_service.redact_for_log(text)
        assert "ghp_" not in result
