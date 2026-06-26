import asyncio
import psutil
from datetime import datetime

from database import (
    save_service_status, get_service_status,
    get_queue_count, get_retry_job_count,
    get_db_size, save_health_event
)
from src.utils.time import now_iso
from src.utils.system import get_memory_info, get_disk_info
from src.utils.config import get_config


class MonitorService:
    def __init__(self):
        self.config = get_config()
        self._running = False
        self._start_time = datetime.utcnow()
        
    async def start(self):
        self._running = True
        save_service_status("monitor", "RUNNING")
        
        while self._running:
            try:
                await self.check_health()
                await asyncio.sleep(self.config.MONITOR_INTERVAL)
            except Exception as e:
                save_health_event("MONITOR_ERROR", "ERROR", str(e))
                await asyncio.sleep(60)
    
    def stop(self):
        self._running = False
        save_service_status("monitor", "STOPPED")
    
    async def check_health(self) -> dict:
        status = {
            "timestamp": now_iso(),
            "uptime_seconds": (datetime.utcnow() - self._start_time).total_seconds(),
            "discord_latency": None,
            "database": "OK",
            "queue_size": get_queue_count(),
            "retry_jobs": get_retry_job_count(),
            "memory_percent": get_memory_info()["percent"],
            "disk_percent": get_disk_info("/")["percent"],
            "db_size": get_db_size(),
            "overall_status": "HEALTHY"
        }
        
        if status["memory_percent"] > self.config.MEMORY_WARNING_THRESHOLD:
            status["overall_status"] = "DEGRADED"
            save_health_event("MEMORY_HIGH", "WARNING", 
                            f"Memory usage at {status['memory_percent']}%")
        
        if status["disk_percent"] > self.config.DISK_WARNING_THRESHOLD:
            status["overall_status"] = "DEGRADED"
            save_health_event("DISK_HIGH", "WARNING",
                            f"Disk usage at {status['disk_percent']}%")
        
        save_service_status("monitor", "RUNNING", heartbeat=True)
        
        return status
    
    def get_status(self) -> dict:
        service = get_service_status("monitor")
        return service if service else {"status": "UNKNOWN"}


monitor_service = MonitorService()
