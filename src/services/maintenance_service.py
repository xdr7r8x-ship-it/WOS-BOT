import asyncio

from src.utils.config import get_config
from src.services.monitor_service import monitor_service
from src.services.watchdog_service import watchdog_service
from src.services.predictive_service import predictive_service
from src.services.resource_guard_service import resource_guard_service
from src.services.log_rotation_service import log_rotation_service


class MaintenanceScheduler:
    def __init__(self):
        self.config = get_config()
        self._running = False
        self._tasks = []
    
    async def start(self):
        self._running = True
        
        monitor_task = asyncio.create_task(monitor_service.start())
        watchdog_task = asyncio.create_task(watchdog_service.start())
        predictive_task = asyncio.create_task(predictive_service.start())
        resource_task = asyncio.create_task(resource_guard_service.start())
        log_task = asyncio.create_task(log_rotation_service.start())
        
        self._tasks = [
            monitor_task,
            watchdog_task,
            predictive_task,
            resource_task,
            log_task,
        ]
    
    async def stop(self):
        self._running = False
        
        monitor_service.stop()
        watchdog_service.stop()
        predictive_service.stop()
        resource_guard_service.stop()
        log_rotation_service.stop()
        
        for task in self._tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


maintenance_scheduler = MaintenanceScheduler()
