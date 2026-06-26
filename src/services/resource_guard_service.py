import asyncio
from pathlib import Path

from database import (
    cleanup_old_health_events, cleanup_old_predictions,
    get_backups
)
from src.utils.config import get_config
from src.utils.system import get_directory_size
from src.services.alert_service import alert_service


class ResourceGuardService:
    def __init__(self):
        self.config = get_config()
        self._running = False
        self._limits = {
            "max_logs_mb": 100,
            "max_backups_mb": 500,
            "max_health_events": 10000,
        }
    
    async def start(self):
        self._running = True
        while self._running:
            try:
                await self.check_resources()
                await asyncio.sleep(self.config.CLEANUP_INTERVAL)
            except Exception:
                await asyncio.sleep(300)
    
    def stop(self):
        self._running = False
    
    async def check_resources(self):
        await self.check_logs_size()
        await self.check_backups_size()
        await self.check_health_events()
        await self.check_database_size()
    
    async def check_logs_size(self):
        logs_dir = Path(self.config.LOGS_DIR)
        if not logs_dir.exists():
            return
        
        size_mb = get_directory_size(logs_dir) / (1024 * 1024)
        
        if size_mb > self._limits["max_logs_mb"]:
            await alert_service.send_alert(
                "LOGS_SIZE_WARNING",
                f"Logs directory is {size_mb:.1f}MB (limit: {self._limits['max_logs_mb']}MB)",
                "WARNING"
            )
            
            from src.services.log_rotation_service import log_rotation_service
            await log_rotation_service.rotate_logs()
    
    async def check_backups_size(self):
        backups_dir = Path(self.config.BACKUP_DIR)
        if not backups_dir.exists():
            return
        
        size_mb = get_directory_size(backups_dir) / (1024 * 1024)
        
        if size_mb > self._limits["max_backups_mb"]:
            await alert_service.send_alert(
                "BACKUPS_SIZE_WARNING",
                f"Backups directory is {size_mb:.1f}MB (limit: {self._limits['max_backups_mb']}MB)",
                "WARNING"
            )
            
            self._rotate_backups()
    
    def _rotate_backups(self):
        backups = get_backups(limit=100)
        if len(backups) > self.config.MAX_BACKUPS:
            for backup in backups[self.config.MAX_BACKUPS:]:
                try:
                    from src.services.backup_service import backup_service
                    backup_service.delete_backup(backup["backup_name"])
                except Exception:
                    pass
    
    async def check_health_events(self):
        from database import get_health_events
        events = get_health_events(limit=10000)
        if len(events) > self._limits["max_health_events"]:
            cleanup_old_health_events()
    
    async def check_database_size(self):
        from database import get_db_size
        size = get_db_size()
        
        try:
            size_mb = float(size.rstrip(" BKMG").replace("KB", "").replace("MB", "").replace("GB", ""))
            unit = size.split()[-1] if len(size.split()) > 1 else "KB"
            if unit == "MB" or "KB" in size:
                if "MB" in size and size_mb > 100:
                    await alert_service.send_alert(
                        "DATABASE_SIZE_WARNING",
                        f"Database is {size}",
                        "WARNING"
                    )
        except Exception:
            pass


resource_guard_service = ResourceGuardService()
