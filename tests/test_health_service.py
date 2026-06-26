import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestHealthService:
    def test_health_service_import(self):
        from src.services.health_service import health_service
        assert health_service is not None

    def test_health_service_has_methods(self):
        from src.services.health_service import health_service
        assert hasattr(health_service, 'get_health')
