import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestAutopilotService:
    def test_autopilot_service_import(self):
        from src.services.autopilot_service import autopilot_service
        assert autopilot_service is not None

    def test_autopilot_service_has_methods(self):
        from src.services.autopilot_service import autopilot_service
        assert hasattr(autopilot_service, 'start')
        assert hasattr(autopilot_service, 'stop')
        assert hasattr(autopilot_service, 'get_status')
        assert hasattr(autopilot_service, 'restart_service')

    def test_get_status(self):
        from src.services.autopilot_service import autopilot_service
        status = autopilot_service.get_status()
        assert "overall_status" in status
        assert "services" in status
