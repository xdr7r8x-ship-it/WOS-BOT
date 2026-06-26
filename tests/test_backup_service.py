import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import DATABASE_PATH


class TestBackupService:
    def test_backup_service_import(self):
        from src.services.backup_service import backup_service
        assert backup_service is not None

    def test_backup_service_has_methods(self):
        from src.services.backup_service import backup_service
        assert hasattr(backup_service, 'create_backup')
        assert hasattr(backup_service, 'list_backups')
        assert hasattr(backup_service, 'get_latest')
        assert hasattr(backup_service, 'delete_backup')
