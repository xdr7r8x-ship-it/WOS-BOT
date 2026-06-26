from database import (
    get_all_guild_ids,
    get_pending_codes,
    get_stuck_processing_codes,
    get_due_retry_jobs,
    update_code_status,
    log_system,
)
from .queue_service import queue_service
from ..utils.logger import bot_logger


class RecoveryService:
    def __init__(self):
        self._logger = bot_logger
        self._stuck_minutes = 20

    async def recover_all(self):
        self._logger.info("Starting recovery process...")
        
        total_pending = 0
        total_stuck = 0
        total_retry_jobs = 0
        
        for guild_id in get_all_guild_ids():
            pending = await self._recover_pending(guild_id)
            stuck = await self._recover_stuck(guild_id)
            retry_jobs = len(get_due_retry_jobs())
            
            total_pending += pending
            total_stuck += stuck
            total_retry_jobs += retry_jobs
        
        report = (
            f"Recovery completed: "
            f"{total_pending} pending codes re-queued, "
            f"{total_stuck} stuck codes recovered, "
            f"{total_retry_jobs} retry jobs pending"
        )
        
        log_system(None, "INFO", "RECOVERY", report)
        self._logger.info(report)
        
        return {
            "pending": total_pending,
            "stuck": total_stuck,
            "retry_jobs": total_retry_jobs
        }

    async def _recover_pending(self, guild_id: str) -> int:
        pending_codes = get_pending_codes(guild_id)
        count = 0
        
        for code_info in pending_codes:
            code_hash = code_info["code_hash"]
            
            if not queue_service.is_processing(guild_id, code_hash):
                queue_service.enqueue(guild_id, code_hash, priority=1)
                count += 1
                self._logger.info(f"Re-queued pending code: {code_hash[:16]}...", guild_id=guild_id)
        
        return count

    async def _recover_stuck(self, guild_id: str) -> int:
        stuck_codes = get_stuck_processing_codes(guild_id, self._stuck_minutes)
        count = 0
        
        for code_info in stuck_codes:
            code_hash = code_info["code_hash"]
            
            update_code_status(guild_id, code_hash, "QUEUED")
            queue_service.enqueue(guild_id, code_hash, priority=2)
            count += 1
            
            self._logger.warning(
                f"Recovered stuck code: {code_hash[:16]}...", 
                guild_id=guild_id
            )
        
        return count


recovery_service = RecoveryService()
