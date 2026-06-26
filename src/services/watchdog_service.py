import asyncio

from database import (
    cleanup_expired_locks, get_all_service_status,
    save_health_event, record_service_failure,
    get_migrations, save_service_status
)
from src.utils.config import get_config
from src.services.alert_service import alert_service


class WatchdogService:
    def __init__(self):
        self.config = get_config()
        self._running = False
        self._max_failures = 3
        
    async def start(self):
        self._running = True
        save_service_status("watchdog", "RUNNING")
        
        while self._running:
            try:
                await self._run_checks()
                await asyncio.sleep(self.config.WATCHDOG_INTERVAL)
            except Exception as e:
                save_health_event("WATCHDOG_ERROR", "ERROR", str(e))
                await asyncio.sleep(60)
    
    def stop(self):
        self._running = False
        save_service_status("watchdog", "STOPPED")
    
    async def _run_checks(self):
        cleaned = cleanup_expired_locks()
        if cleaned > 0:
            save_health_event("LOCK_CLEANUP", "INFO", f"Cleaned {cleaned} expired locks")
        
        services = get_all_service_status()
        for service in services:
            name = service.get("service_name")
            if not name or name in ["watchdog", "autopilot"]:
                continue
            
            status = service.get("status")
            failures = service.get("consecutive_failures", 0)
            
            if failures >= self._max_failures:
                save_health_event("SERVICE_FATAL", "ERROR",
                    f"Service {name} failed {failures} times")
                await alert_service.send_alert(
                    "Service Failure",
                    f"Service {name} has failed {failures} consecutive times",
                    "WARNING"
                )
        
        migrations = get_migrations()
        for migration in migrations:
            if migration.get("status") == "RUNNING":
                save_health_event("STUCK_MIGRATION", "WARNING",
                    f"Migration {migration.get('migration_id')} is stuck")
        
        save_service_status("watchdog", "RUNNING", heartbeat=True)
    
    def get_status(self) -> dict:
        services = get_all_service_status()
        return {
            "services": services,
            "expired_locks_cleaned": 0
        }


watchdog_service = WatchdogService()
