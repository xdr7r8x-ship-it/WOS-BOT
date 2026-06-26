import asyncio
from datetime import datetime

from database import (
    cleanup_old_data,
    get_all_guild_ids,
    get_gift_codes_to_delete,
    delete_gift_code,
    log_system,
)
from ..utils.logger import bot_logger


class CleanupService:
    def __init__(self):
        self._running = False
        self._interval = 6 * 60 * 60
        self._logger = bot_logger

    async def cleanup(self):
        if self._running:
            return
        
        self._running = True
        try:
            self._logger.info("Starting cleanup...")
            
            cleanup_old_data()
            
            for guild_id in get_all_guild_ids():
                log_system(
                    guild_id, "INFO", "CLEANUP", 
                    "Cleanup completed successfully"
                )
            
            self._logger.info("Cleanup completed")
            
        except Exception as e:
            self._logger.error(f"Cleanup error: {e}")
        finally:
            self._running = False

    async def start(self):
        while True:
            await asyncio.sleep(self._interval)
            try:
                await self.cleanup()
            except Exception as e:
                self._logger.error(f"Cleanup service error: {e}")

    async def run_once(self):
        await self.cleanup()


cleanup_service = CleanupService()
