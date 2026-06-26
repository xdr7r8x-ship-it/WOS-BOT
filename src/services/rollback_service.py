import shutil
from pathlib import Path
from typing import Optional

from database import get_latest_backup, save_update_history
from src.services.backup_service import backup_service


class RollbackService:
    def __init__(self):
        self.current_backup = None
        
    def restore_latest_backup(self) -> tuple[bool, str]:
        backup = get_latest_backup()
        
        if not backup:
            return False, "No backup available"
        
        backup_path = Path(backup["backup_path"])
        if not backup_path.exists():
            return False, "Backup path not found"
        
        try:
            db_dir = Path("db")
            if db_dir.exists():
                for f in db_dir.glob("*.db*"):
                    try:
                        f.unlink()
                    except Exception:
                        pass
            
            db_backup = backup_path / "db"
            if db_backup.exists():
                for f in db_backup.glob("*.db*"):
                    shutil.copy2(f, db_dir / f.name)
            
            for item in ["VERSION", "main.py", "database.py", "requirements.txt"]:
                src = backup_path / item
                if src.exists():
                    shutil.copy2(src, item)
            
            src_backup = backup_path / "src"
            if src_backup.exists():
                shutil.copytree(src_backup, "src", dirs_exist_ok=True)
            
            save_update_history(
                backup.get("backup_name", "unknown"),
                "previous",
                "ROLLBACK",
                f"Restored from backup {backup['backup_name']}"
            )
            
            return True, f"Restored from {backup['backup_name']}"
            
        except Exception as e:
            return False, str(e)
    
    def can_rollback(self) -> bool:
        backup = get_latest_backup()
        return backup is not None and Path(backup["backup_path"]).exists()


rollback_service = RollbackService()
