import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestAPIGuardService:
    def test_api_guard_import(self):
        from src.services.api_guard_service import api_guard_service
        assert api_guard_service is not None
    
    def test_api_guard_has_methods(self):
        from src.services.api_guard_service import api_guard_service
        assert hasattr(api_guard_service, 'safe_request')
        assert hasattr(api_guard_service, 'is_circuit_open')
        assert hasattr(api_guard_service, 'reset_circuit')
    
    def test_is_circuit_open_initially_false(self):
        from src.services.api_guard_service import api_guard_service
        assert api_guard_service.is_circuit_open() is False
    
    def test_reset_circuit(self):
        from src.services.api_guard_service import api_guard_service
        api_guard_service.reset_circuit()
        assert api_guard_service.is_circuit_open() is False
    
    def test_sanitize_headers_removes_auth(self):
        from src.services.api_guard_service import api_guard_service
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer secret_token",
            "X-API-Key": "secret_key"
        }
        safe = api_guard_service._sanitize_headers(headers)
        assert "Authorization" not in safe
        assert "X-API-Key" not in safe
        assert "Content-Type" in safe
    
    def test_safe_log_response(self):
        from src.services.api_guard_service import api_guard_service
        data = {"token": "secret123", "user": "test"}
        result = api_guard_service.safe_log_response(data)
        assert "secret123" not in str(result)
    
    def test_safe_log_error(self):
        from src.services.api_guard_service import api_guard_service
        error = "Error with GitHub token: ghp_abcdefghij1234567890klmnopqrstuvwx"
        result = api_guard_service.safe_log_error(error)
        assert "ghp_" not in result
