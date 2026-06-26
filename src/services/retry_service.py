import asyncio
from datetime import datetime, timedelta

from database import (
    get_due_retry_jobs,
    update_retry_job,
    save_redemption,
    redemption_exists,
)
from ..api.redeem import WhiteoutAPI
from ..utils.errors import ErrorType, is_retryable, get_redemption_status
from ..utils.logger import bot_logger
from ..utils.rate_limit import rate_limiter


MAX_RETRIES = 5
BACKOFFS = [2, 5, 10, 20, 45]


class RetryService:
    def __init__(self):
        self._running = False
        self._interval = 60
        self._logger = bot_logger
        self._api = WhiteoutAPI()

    async def process_retry_jobs(self):
        if self._running:
            return
        
        self._running = True
        try:
            jobs = get_due_retry_jobs(limit=100)
            
            for job in jobs:
                guild_id = job["guild_id"]
                code_hash = job["code_hash"]
                player_id = job["player_id"]
                reason = job["reason"]
                job_id = job["id"]
                attempts = job["attempts"]
                
                if attempts >= MAX_RETRIES:
                    update_retry_job(job_id, "FAILED")
                    save_redemption(guild_id, code_hash, player_id, "FAILED", reason, attempts)
                    self._logger.warning(f"Retry job failed after max attempts", guild_id=guild_id)
                    continue
                
                update_retry_job(job_id, "RUNNING")
                
                if rate_limiter.is_paused(guild_id)[0]:
                    backoff_idx = min(attempts, len(BACKOFFS) - 1)
                    next_retry = (datetime.utcnow() + timedelta(seconds=BACKOFFS[backoff_idx])).isoformat()
                    update_retry_job(job_id, "PENDING", next_retry)
                    continue
                
                try:
                    response, error = await self._api.redeem(player_id, code_hash)
                    
                    if error and is_retryable(error):
                        rate_limiter.record_failure(guild_id, error.value)
                        
                        if rate_limiter.is_paused(guild_id)[0]:
                            update_retry_job(job_id, "PENDING", 
                                (datetime.utcnow() + timedelta(minutes=10)).isoformat())
                            self._logger.warning(f"API paused for guild {guild_id}", guild_id=guild_id)
                            continue
                        
                        backoff_idx = min(attempts, len(BACKOFFS) - 1)
                        next_retry = (datetime.utcnow() + timedelta(seconds=BACKOFFS[backoff_idx])).isoformat()
                        update_retry_job(job_id, "PENDING", next_retry)
                        continue
                    
                    if response.get("code") == 200:
                        update_retry_job(job_id, "DONE")
                        save_redemption(guild_id, code_hash, player_id, "SUCCESS", None, attempts + 1)
                        self._logger.info(f"Retry successful for {player_id}", guild_id=guild_id)
                    else:
                        msg = response.get("msg", "").lower()
                        
                        if "already" in msg or "redeemed" in msg:
                            update_retry_job(job_id, "DONE")
                            save_redemption(guild_id, code_hash, player_id, "ALREADY_REDEEMED", None, attempts + 1)
                        elif "expired" in msg or "time" in msg:
                            update_retry_job(job_id, "DONE")
                            save_redemption(guild_id, code_hash, player_id, "EXPIRED_CODE", None, attempts + 1)
                        elif "invalid" in msg or "not found" in msg:
                            update_retry_job(job_id, "DONE")
                            save_redemption(guild_id, code_hash, player_id, "INVALID_CODE", None, attempts + 1)
                        else:
                            update_retry_job(job_id, "FAILED")
                            save_redemption(guild_id, code_hash, player_id, "FAILED", reason, attempts + 1)
                            
                except Exception as e:
                    self._logger.error(f"Retry error: {e}", guild_id=guild_id)
                    backoff_idx = min(attempts, len(BACKOFFS) - 1)
                    next_retry = (datetime.utcnow() + timedelta(seconds=BACKOFFS[backoff_idx])).isoformat()
                    update_retry_job(job_id, "PENDING", next_retry)
                
                await asyncio.sleep(0.5)
                
        finally:
            self._running = False

    async def start(self):
        while True:
            try:
                await self.process_retry_jobs()
            except Exception as e:
                self._logger.error(f"Retry service error: {e}")
            
            await asyncio.sleep(self._interval)

    async def run_once(self):
        await self.process_retry_jobs()


retry_service = RetryService()
