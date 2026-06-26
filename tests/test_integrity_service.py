import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestIntegrityService:
    def test_integrity_service_import(self):
        from src.services.integrity_service import integrity_service
        assert integrity_service is not None

    def test_check_required_files(self):
        from src.services.integrity_service import integrity_service
        result = integrity_service.check_required_files()
        assert "status" in result
        assert result["status"] in ["PASS", "FAIL"]

    def test_check_required_directories(self):
        from src.services.integrity_service import integrity_service
        result = integrity_service.check_required_directories()
        assert "status" in result

    def test_run_integrity_check(self):
        from src.services.integrity_service import integrity_service
        result = integrity_service.run_integrity_check()
        assert "overall_status" in result
        assert "checks" in result
