import asyncio

from database import (
    save_service_status, get_all_service_status,
    get_service_status, record_service_failure,
    reset_service_failures, save_health_event
)
from src.services.monitor_service import monitor_service
from src.services.watchdog_service import watchdog_service
from src.services.predictive_service import predictive_service
from src.services.resource_guard_service import resource_guard_service
from src.services.log_rotation_service import log_rotation_service
from src.services.alert_service import alert_service


MAX_CONSECUTIVE_FAILURES = 3


class AutopilotService:
    def __init__(self):
        self._running = False
        self._services = {}
        self._service_tasks = {}
    
    async def start(self):
        self._running = True
        save_service_status("autopilot", "RUNNING")
        
        services = [
            ("monitor", monitor_service),
            ("watchdog", watchdog_service),
            ("predictive", predictive_service),
            ("resource_guard", resource_guard_service),
            ("log_rotation", log_rotation_service),
        ]
        
        for name, service in services:
            self._services[name] = service
            save_service_status(name, "STARTING")
            
            try:
                if hasattr(service, 'start'):
                    task = asyncio.create_task(service.start())
                else:
                    task = asyncio.create_task(asyncio.sleep(float('inf')))
                
                self._service_tasks[name] = task
                save_service_status(name, "RUNNING")
                
            except Exception as e:
                save_health_event("SERVICE_START_FAILED", "ERROR",
                    f"Failed to start {name}: {e}")
                save_service_status(name, "FAILED")
    
    async def stop(self):
        self._running = False
        save_service_status("autopilot", "STOPPING")
        
        for name, service in self._services.items():
            try:
                if hasattr(service, 'stop'):
                    service.stop()
            except Exception:
                pass
        
        for task in self._service_tasks.values():
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        save_service_status("autopilot", "STOPPED")
    
    def get_status(self) -> dict:
        services = get_all_service_status()
        
        overall = "HEALTHY"
        for svc in services:
            if svc.get("consecutive_failures", 0) >= MAX_CONSECUTIVE_FAILURES:
                overall = "DEGRADED"
                break
            if svc.get("status") == "FAILED":
                overall = "UNHEALTHY"
                break
        
        return {
            "overall_status": overall,
            "services": {
                s.get("service_name"): {
                    "status": s.get("status"),
                    "consecutive_failures": s.get("consecutive_failures", 0),
                    "restart_count": s.get("restart_count", 0),
                    "last_heartbeat": s.get("last_heartbeat")
                }
                for s in services
            }
        }
    
    async def restart_service(self, name: str) -> bool:
        if name not in self._services:
            return False
        
        service = self._services[name]
        
        if name in self._service_tasks:
            old_task = self._service_tasks[name]
            if not old_task.done():
                old_task.cancel()
                try:
                    await old_task
                except asyncio.CancelledError:
                    pass
        
        record_service_failure(name)
        
        try:
            if hasattr(service, 'start'):
                task = asyncio.create_task(service.start())
            else:
                task = asyncio.create_task(asyncio.sleep(float('inf')))
            
            self._service_tasks[name] = task
            reset_service_failures(name)
            save_service_status(name, "RUNNING")
            
            save_health_event("SERVICE_RESTARTED", "INFO", f"Service {name} restarted")
            
            return True
            
        except Exception as e:
            save_health_event("SERVICE_RESTART_FAILED", "ERROR",
                f"Failed to restart {name}: {e}")
            return False


autopilot_service = AutopilotService()
