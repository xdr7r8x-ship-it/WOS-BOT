import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestAbuseGuardService:
    def test_abuse_guard_import(self):
        from src.services.abuse_guard_service import abuse_guard_service
        assert abuse_guard_service is not None
    
    def test_abuse_guard_has_methods(self):
        from src.services.abuse_guard_service import abuse_guard_service
        assert hasattr(abuse_guard_service, 'check_register_rate_limit')
        assert hasattr(abuse_guard_service, 'check_redeem_rate_limit')
        assert hasattr(abuse_guard_service, 'is_user_blocked')
    
    def test_check_register_rate_limit_first_attempt(self):
        from src.services.abuse_guard_service import abuse_guard_service
        allowed, status = abuse_guard_service.check_register_rate_limit("guild1", "user1")
        assert allowed is True
        assert status == "OK"
    
    def test_is_user_blocked_initially_false(self):
        from src.services.abuse_guard_service import abuse_guard_service
        blocked = abuse_guard_service.is_user_blocked("guild1", "user1")
        assert blocked is False
    
    def test_check_command_rate_limit_db(self):
        from src.services.abuse_guard_service import abuse_guard_service
        allowed, count = abuse_guard_service.check_command_rate_limit_db(
            "guild1", "user1", "test_cmd", max_count=5, window_seconds=60
        )
        assert allowed is True
        assert count >= 1
    
    def test_check_redeem_rate_limit(self):
        from src.services.abuse_guard_service import abuse_guard_service
        allowed, status = abuse_guard_service.check_redeem_rate_limit("guild1", "user1")
        assert allowed is True
        assert status in ["OK", "RATE_LIMITED"]
