import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestMigrationService:
    def test_migration_service_import(self):
        from src.services.migration_service import migration_service
        assert migration_service is not None

    def test_migration_service_has_methods(self):
        from src.services.migration_service import migration_service
        assert hasattr(migration_service, 'register')
        assert hasattr(migration_service, 'run_migration')
        assert hasattr(migration_service, 'run_all_pending')
        assert hasattr(migration_service, 'get_applied')
