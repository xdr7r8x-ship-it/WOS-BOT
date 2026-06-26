import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


class TestFileGuardService:
    def test_file_guard_import(self):
        from src.services.file_guard_service import file_guard_service
        assert file_guard_service is not None
    
    def test_file_guard_has_methods(self):
        from src.services.file_guard_service import file_guard_service
        assert hasattr(file_guard_service, 'is_safe_for_backup')
        assert hasattr(file_guard_service, 'scan_backup_directory')
        assert hasattr(file_guard_service, 'get_safe_filename')
    
    def test_is_safe_for_backup_env(self):
        from src.services.file_guard_service import file_guard_service
        from pathlib import Path
        result = file_guard_service.is_safe_for_backup(Path(".env"))
        assert result is False
    
    def test_is_safe_for_backup_py_file(self):
        from src.services.file_guard_service import file_guard_service
        from pathlib import Path
        result = file_guard_service.is_safe_for_backup(Path("main.py"))
        assert result is True
    
    def test_get_safe_filename(self):
        from src.services.file_guard_service import file_guard_service
        result = file_guard_service.get_safe_filename("../../../etc/passwd")
        assert "/" not in result
    
    def test_ensure_directory_safe_logs(self):
        from src.services.file_guard_service import file_guard_service
        from pathlib import Path
        result = file_guard_service.ensure_directory_safe(Path("logs"))
        assert result is True
    
    def test_cleanup_temp_files_nonexistent_dir(self):
        from src.services.file_guard_service import file_guard_service
        from pathlib import Path
        result = file_guard_service.cleanup_temp_files(Path("/nonexistent/directory"))
        assert result == 0
