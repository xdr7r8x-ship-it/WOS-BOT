import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestWatchdogService:
    def test_watchdog_service_import(self):
        from src.services.watchdog_service import watchdog_service
        assert watchdog_service is not None

    def test_watchdog_service_has_methods(self):
        from src.services.watchdog_service import watchdog_service
        assert hasattr(watchdog_service, 'start')
        assert hasattr(watchdog_service, 'stop')
        assert hasattr(watchdog_service, 'get_status')
