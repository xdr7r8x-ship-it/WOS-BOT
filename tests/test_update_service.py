import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestUpdateService:
    def test_update_service_import(self):
        from src.services.update_service import update_service
        assert update_service is not None

    def test_update_service_has_methods(self):
        from src.services.update_service import update_service
        assert hasattr(update_service, 'check_for_updates')
        assert hasattr(update_service, 'create_update_plan')
        assert hasattr(update_service, 'apply_update')

    def test_create_update_plan_no_url(self):
        from src.services.update_service import update_service
        plan = update_service.create_update_plan()
        assert "can_update" in plan
