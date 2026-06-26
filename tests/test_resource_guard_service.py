import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestResourceGuardService:
    def test_resource_guard_import(self):
        from src.services.resource_guard_service import resource_guard_service
        assert resource_guard_service is not None

    def test_resource_guard_has_methods(self):
        from src.services.resource_guard_service import resource_guard_service
        assert hasattr(resource_guard_service, 'start')
        assert hasattr(resource_guard_service, 'stop')
        assert hasattr(resource_guard_service, 'check_resources')
