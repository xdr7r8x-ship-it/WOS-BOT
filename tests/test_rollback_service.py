import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import DATABASE_PATH


class TestRollbackService:
    @pytest.fixture(autouse=True)
    def setup_database(self):
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()
        from database import init_database, init_autopilot_tables
        init_database()
        init_autopilot_tables()
        yield
        if DATABASE_PATH.exists():
            DATABASE_PATH.unlink()

    def test_rollback_service_import(self):
        from src.services.rollback_service import rollback_service
        assert rollback_service is not None

    def test_rollback_service_has_methods(self):
        from src.services.rollback_service import rollback_service
        assert hasattr(rollback_service, 'restore_latest_backup')
        assert hasattr(rollback_service, 'can_rollback')

    def test_can_rollback_no_backup(self):
        from src.services.rollback_service import rollback_service
        assert rollback_service.can_rollback() is False
