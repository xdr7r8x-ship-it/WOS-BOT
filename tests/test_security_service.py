import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestSecurityService:
    def test_security_service_import(self):
        from src.services.security_service import security_service
        assert security_service is not None

    def test_run_security_scan(self):
        from src.services.security_service import security_service
        result = security_service.run_security_scan()
        assert "overall_status" in result
        assert "checks" in result
