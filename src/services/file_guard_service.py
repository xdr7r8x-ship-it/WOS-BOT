import os
import shutil
from pathlib import Path
from typing import Optional

from src.utils.security import sanitize_filename, is_safe_path
from src.services.secret_guard_service import secret_guard_service


EXCLUDED_FROM_BACKUP = {".env", ".env.local", ".env.example", "venv", "node_modules", "__pycache__", ".git"}


class FileGuardService:
    def __init__(self):
        self.backup_dir = Path("backups")
        self.logs_dir = Path("logs")
        
    def is_safe_for_backup(self, file_path: Path) -> bool:
        if not file_path.exists():
            return False
        
        name = file_path.name
        
        if name in EXCLUDED_FROM_BACKUP:
            return False
        
        if name.startswith(".env"):
            return False
        
        return True
    
    def is_safe_write_location(self, file_path: Path, allowed_dir: str) -> bool:
        try:
            return is_safe_path(str(file_path), allowed_dir)
        except Exception:
            return False
    
    def scan_backup_directory(self, backup_path: Path) -> tuple[bool, list]:
        violations = []
        
        for excluded in EXCLUDED_FROM_BACKUP:
            check_path = backup_path / excluded
            if check_path.exists():
                violations.append(str(check_path))
        
        has_secrets, secret_files = secret_guard_service.check_backup_for_secrets(backup_path)
        if has_secrets:
            violations.extend(secret_files)
        
        return len(violations) > 0, violations
    
    def cleanup_temp_files(self, directory: Path, max_age_seconds: int = 3600):
        if not directory.exists():
            return 0
        
        import time
        removed = 0
        now = time.time()
        
        for file in directory.glob("*.tmp"):
            try:
                if now - file.stat().st_mtime > max_age_seconds:
                    file.unlink()
                    removed += 1
            except Exception:
                pass
        
        return removed
    
    def ensure_directory_safe(self, directory: Path) -> bool:
        try:
            directory.mkdir(parents=True, exist_ok=True)
            
            test_file = directory / ".write_test"
            test_file.touch()
            test_file.unlink()
            
            return True
        except Exception:
            return False
    
    def get_safe_filename(self, filename: str) -> str:
        return sanitize_filename(filename)
    
    def verify_backup_integrity(self, backup_path: Path) -> tuple[bool, str]:
        if not backup_path.exists():
            return False, "Backup path does not exist"
        
        has_violations, violations = self.scan_backup_directory(backup_path)
        
        if has_violations:
            return False, f"Security violations found: {', '.join(violations)}"
        
        return True, "OK"
    
    def delete_unsafe_backup(self, backup_path: Path) -> bool:
        try:
            if backup_path.exists():
                shutil.rmtree(backup_path)
            return True
        except Exception:
            return False


file_guard_service = FileGuardService()
