import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional

from database import save_backup, get_backups, get_latest_backup
from src.utils.config import get_config
from src.utils.system import get_directory_size


BACKUP_EXCLUDE = {".env", ".env.example", "venv", "node_modules", "__pycache__", ".git"}


class BackupService:
    def __init__(self):
        self.config = get_config()
        self.backup_dir = Path(self.config.BACKUP_DIR)
        self.max_backups = self.config.MAX_BACKUPS
        
    def ensure_backup_dir(self):
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self) -> tuple[bool, str]:
        self.ensure_backup_dir()
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        try:
            backup_path.mkdir(exist_ok=True)
            
            db_backup = backup_path / "db"
            db_backup.mkdir()
            
            db_source = Path("db")
            if db_source.exists():
                for f in db_source.glob("*.db*"):
                    shutil.copy2(f, db_backup / f.name)
            
            for item in Path(".").iterdir():
                if item.name in BACKUP_EXCLUDE or item.name.startswith("."):
                    continue
                if item.is_dir() and item.name not in ["db", "backups", "logs"]:
                    continue
                    
            files_to_backup = ["VERSION", "main.py", "database.py", "requirements.txt"]
            for fname in files_to_backup:
                src = Path(fname)
                if src.exists():
                    shutil.copy2(src, backup_path / fname)
            
            shutil.copytree(Path("src"), backup_path / "src", dirs_exist_ok=True)
            shutil.copytree(Path("tests"), backup_path / "tests", dirs_exist_ok=True)
            
            size = get_directory_size(backup_path)
            
            backup_id = save_backup(backup_name, str(backup_path), size)
            
            self.rotate_backups()
            
            return True, str(backup_path)
            
        except Exception as e:
            save_backup(backup_name, str(backup_path), 0, "FAILED")
            return False, str(e)
    
    def rotate_backups(self):
        backups = get_backups(limit=100)
        
        if len(backups) <= self.max_backups:
            return
        
        for backup in backups[self.max_backups:]:
            try:
                path = Path(backup["backup_path"])
                if path.exists():
                    shutil.rmtree(path)
            except Exception:
                pass
    
    def list_backups(self) -> list:
        return get_backups(limit=self.max_backups)
    
    def get_latest(self) -> Optional[dict]:
        return get_latest_backup()
    
    def delete_backup(self, backup_name: str) -> bool:
        backups = get_backups(limit=100)
        for backup in backups:
            if backup["backup_name"] == backup_name:
                try:
                    path = Path(backup["backup_path"])
                    if path.exists():
                        shutil.rmtree(path)
                    return True
                except Exception:
                    return False
        return False


backup_service = BackupService()
