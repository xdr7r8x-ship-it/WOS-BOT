import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional

from database import (
    get_active_players,
    redemption_exists,
    save_redemption,
    update_code_status,
    add_retry_job,
    get_redemption_count,
    save_processed_code,
    delete_gift_code,
    get_code_by_hash,
    generate_code_hash,
    log_system,
)
from ..api.redeem import WhiteoutAPI
from ..utils.errors import ErrorType, RedemptionStatus, is_retryable, is_final_error
from ..utils.logger import bot_logger
from ..utils.rate_limit import rate_limiter


MAX_RETRIES = 5
BACKOFFS = [2, 5, 10, 20, 45]


class RedeemService:
    def __init__(self):
        self._api = WhiteoutAPI()
        self._logger = bot_logger
        self._processing_codes = set()

    async def process_code(self, guild_id: str, code: str, message_id: str = None):
        code_hash = generate_code_hash(guild_id, code)
        
        if code_hash in self._processing_codes:
            return
        
        self._processing_codes.add(code_hash)
        
        try:
            update_code_status(guild_id, code_hash, "PROCESSING")
            
            code_info = get_code_by_hash(guild_id, code_hash)
            if not code_info:
                self._logger.error(f"Code not found: {code_hash}", guild_id=guild_id)
                return
            
            players = get_active_players(guild_id)
            
            if not players:
                self._finish_processing(guild_id, code_hash, code, [], {})
                return
            
            results = {
                "success": 0,
                "failed": 0,
                "retry_later": 0,
                "verification": 0,
                "skipped": 0,
            }
            
            player_results = []
            
            for player_id in players:
                if redemption_exists(guild_id, code_hash, player_id):
                    results["skipped"] += 1
                    continue
                
                status, error_type = await self._redeem_for_player(guild_id, code, code_hash, player_id)
                
                if status == RedemptionStatus.SUCCESS:
                    results["success"] += 1
                elif status == RedemptionStatus.NEEDS_VERIFICATION:
                    results["verification"] += 1
                elif status == RedemptionStatus.RETRY_LATER:
                    results["retry_later"] += 1
                elif status == RedemptionStatus.SKIPPED_DUPLICATE:
                    results["skipped"] += 1
                else:
                    results["failed"] += 1
                
                player_results.append({"player_id": player_id, "status": status.value})
                
                await asyncio.sleep(random.uniform(0.5, 1.5))
            
            self._finish_processing(guild_id, code_hash, code, players, results)
            
        except Exception as e:
            self._logger.error(f"Process code error: {e}", guild_id=guild_id)
            update_code_status(guild_id, code_hash, "FAILED")
        finally:
            self._processing_codes.discard(code_hash)

    async def _redeem_for_player(
        self, guild_id: str, code: str, code_hash: str, player_id: str
    ) -> tuple[RedemptionStatus, Optional[ErrorType]]:
        attempt = 0
        
        while attempt < MAX_RETRIES:
            if rate_limiter.is_paused(guild_id)[0]:
                await asyncio.sleep(5)
                continue
            
            try:
                response, error = await self._api.redeem(player_id, code)
                
                if error:
                    rate_limiter.record_failure(guild_id, error.value)
                    
                    if rate_limiter.is_paused(guild_id)[0]:
                        save_redemption(guild_id, code_hash, player_id, "RETRY_LATER", error.value, attempt + 1)
                        self._schedule_retry(guild_id, code_hash, player_id, error.value)
                        return RedemptionStatus.RETRY_LATER, error
                    
                    if is_retryable(error):
                        attempt += 1
                        backoff = BACKOFFS[min(attempt - 1, len(BACKOFFS) - 1)]
                        await asyncio.sleep(backoff)
                        continue
                    
                    save_redemption(guild_id, code_hash, player_id, error.value, error.value, attempt + 1)
                    return self._error_to_status(error), error
                
                code_response = response.get("code")
                
                if code_response == 200:
                    save_redemption(guild_id, code_hash, player_id, "SUCCESS", None, attempt + 1)
                    return RedemptionStatus.SUCCESS, None
                
                msg = response.get("msg", "").lower() if response.get("msg") else ""
                
                if "already" in msg and ("redeem" in msg or "received" in msg):
                    save_redemption(guild_id, code_hash, player_id, "ALREADY_REDEEMED", None, attempt + 1)
                    return RedemptionStatus.ALREADY_REDEEMED, None
                
                if "expired" in msg or "time" in msg:
                    save_redemption(guild_id, code_hash, player_id, "EXPIRED_CODE", None, attempt + 1)
                    return RedemptionStatus.EXPIRED_CODE, None
                
                if "invalid" in msg or "not found" in msg or "cdk" in msg:
                    save_redemption(guild_id, code_hash, player_id, "INVALID_CODE", None, attempt + 1)
                    return RedemptionStatus.INVALID_CODE, None
                
                if "captcha" in msg or "human" in msg or "verify" in msg:
                    save_redemption(guild_id, code_hash, player_id, "NEEDS_VERIFICATION", "CAPTCHA_REQUIRED", attempt + 1)
                    return RedemptionStatus.NEEDS_VERIFICATION, ErrorType.CAPTCHA_REQUIRED
                
                if "limit" in msg:
                    save_redemption(guild_id, code_hash, player_id, "RATE_LIMITED", None, attempt + 1)
                    return RedemptionStatus.RATE_LIMITED, None
                
                save_redemption(guild_id, code_hash, player_id, "FAILED", "UNKNOWN_ERROR", attempt + 1)
                return RedemptionStatus.FAILED, None
                
            except Exception as e:
                self._logger.error(f"Redeem error for {player_id}: {e}", guild_id=guild_id)
                attempt += 1
                if attempt < MAX_RETRIES:
                    backoff = BACKOFFS[min(attempt - 1, len(BACKOFFS) - 1)]
                    await asyncio.sleep(backoff)
        
        save_redemption(guild_id, code_hash, player_id, "FAILED", "MAX_RETRIES", MAX_RETRIES)
        self._schedule_retry(guild_id, code_hash, player_id, "MAX_RETRIES")
        return RedemptionStatus.FAILED, None

    def _schedule_retry(self, guild_id: str, code_hash: str, player_id: str, reason: str):
        next_retry = (datetime.utcnow() + timedelta(seconds=30)).isoformat()
        add_retry_job(guild_id, code_hash, player_id, reason, next_retry)

    def _error_to_status(self, error: ErrorType) -> RedemptionStatus:
        mapping = {
            ErrorType.INVALID_CODE: RedemptionStatus.INVALID_CODE,
            ErrorType.EXPIRED_CODE: RedemptionStatus.EXPIRED_CODE,
            ErrorType.ALREADY_REDEEMED: RedemptionStatus.ALREADY_REDEEMED,
            ErrorType.CAPTCHA_REQUIRED: RedemptionStatus.NEEDS_VERIFICATION,
            ErrorType.HUMAN_VERIFICATION_REQUIRED: RedemptionStatus.NEEDS_VERIFICATION,
        }
        return mapping.get(error, RedemptionStatus.FAILED)

    def _finish_processing(
        self, guild_id: str, code_hash: str, code: str, players: list, results: dict
    ):
        counts = get_redemption_count(guild_id, code_hash)
        
        total = len(players)
        success = counts.get("success", 0)
        failed = counts.get("failed", 0) + counts.get("needs_verification", 0)
        retry = 0
        verification = counts.get("needs_verification", 0)
        
        final_status = "COMPLETED"
        if failed > 0 and success == 0:
            final_status = "FAILED"
        elif verification > 0 and success == 0:
            final_status = "NEEDS_VERIFICATION"
        
        save_processed_code(
            guild_id=guild_id,
            code_hash=code_hash,
            final_status=final_status,
            total_players=total,
            success_count=success,
            failed_count=failed,
            retry_count=retry,
            verification_count=verification,
        )
        
        update_code_status(guild_id, code_hash, final_status)
        
        delete_gift_code(guild_id, code_hash)
        
        self._logger.info(
            f"Code {code_hash[:16]}... finished: {success} success, {failed} failed, {verification} verification",
            guild_id=guild_id
        )


redeem_service = RedeemService()
