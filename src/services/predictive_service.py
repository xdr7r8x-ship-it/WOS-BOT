import asyncio
from pathlib import Path

from database import (
    save_prediction_event, get_prediction_events,
    get_retry_job_count, cleanup_old_predictions
)
from src.utils.config import get_config
from src.utils.system import get_memory_usage_percent, get_disk_usage_percent
from src.services.alert_service import alert_service


class PredictiveService:
    def __init__(self):
        self.config = get_config()
        self._running = False
        self._thresholds = {
            "memory_warning": 80,
            "memory_critical": 90,
            "disk_warning": 85,
            "disk_critical": 95,
        }
        
    async def start(self):
        self._running = True
        while self._running:
            try:
                await self.scan()
                await asyncio.sleep(self.config.PREDICTION_INTERVAL)
            except Exception:
                await asyncio.sleep(60)
    
    def stop(self):
        self._running = False
    
    async def scan(self):
        alerts = []
        
        memory = get_memory_usage_percent()
        if memory > self._thresholds["memory_critical"]:
            alerts.append(("MEMORY_CRITICAL", "ERROR", f"Memory at {memory}%"))
        elif memory > self._thresholds["memory_warning"]:
            alerts.append(("MEMORY_HIGH", "WARNING", f"Memory at {memory}%"))
        
        disk = get_disk_usage_percent("/")
        if disk > self._thresholds["disk_critical"]:
            alerts.append(("DISK_CRITICAL", "ERROR", f"Disk at {disk}%"))
        elif disk > self._thresholds["disk_warning"]:
            alerts.append(("DISK_HIGH", "WARNING", f"Disk at {disk}%"))
        
        retry_count = get_retry_job_count()
        if retry_count > 100:
            alerts.append(("RETRY_QUEUE_HIGH", "WARNING", f"Retry queue at {retry_count}"))
        
        for alert_type, severity, message in alerts:
            save_prediction_event(alert_type, severity, message)
            
            if severity == "ERROR":
                await alert_service.send_alert(alert_type, message, severity)
                
                if alert_type == "DISK_HIGH":
                    from src.services.cleanup_service import cleanup_service
                    await cleanup_service.run_once()
    
    def get_predictions(self, limit: int = 50) -> list:
        return get_prediction_events(limit)
    
    def get_active_predictions(self) -> list:
        events = get_prediction_events(limit=100)
        return [e for e in events if e.get("severity") in ("WARNING", "ERROR")]


predictive_service = PredictiveService()
