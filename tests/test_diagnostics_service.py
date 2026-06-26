import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestDiagnosticsService:
    def test_diagnostics_service_import(self):
        from src.services.diagnostics_service import diagnostics_service
        assert diagnostics_service is not None

    def test_check_python_version(self):
        from src.services.diagnostics_service import diagnostics_service
        result = diagnostics_service.check_python_version()
        assert "status" in result
        assert result["status"] in ["PASS", "FAIL"]

    def test_check_env_file(self):
        from src.services.diagnostics_service import diagnostics_service
        result = diagnostics_service.check_env_file()
        assert "status" in result

    def test_check_bot_token(self):
        from src.services.diagnostics_service import diagnostics_service
        result = diagnostics_service.check_bot_token()
        assert "status" in result

    def test_check_database(self):
        from src.services.diagnostics_service import diagnostics_service
        result = diagnostics_service.check_database()
        assert "status" in result

    def test_check_wal_mode(self):
        from src.services.diagnostics_service import diagnostics_service
        result = diagnostics_service.check_wal_mode()
        assert "status" in result

    def test_check_version_file(self):
        from src.services.diagnostics_service import diagnostics_service
        result = diagnostics_service.check_version_file()
        assert "status" in result
