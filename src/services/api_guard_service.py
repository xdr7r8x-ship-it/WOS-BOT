import asyncio
import aiohttp
from typing import Optional
import logging

from src.utils.redaction import redact_dict, redact_text


logger = logging.getLogger(__name__)


class APIGuardService:
    def __init__(self):
        self._circuit_open = False
        self._failure_count = 0
        self._failure_threshold = 5
        self._circuit_timeout = 60
        self.default_timeout = 30
        
    async def safe_request(
        self,
        method: str,
        url: str,
        headers: dict = None,
        json_data: dict = None,
        timeout: int = None,
        max_retries: int = 3
    ) -> tuple[bool, dict, str]:
        if self._circuit_open:
            return False, {}, "Circuit breaker open"
        
        if timeout is None:
            timeout = self.default_timeout
        
        safe_headers = self._sanitize_headers(headers) if headers else {}
        
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.request(
                        method,
                        url,
                        headers=safe_headers,
                        json=json_data,
                        timeout=aiohttp.ClientTimeout(total=timeout)
                    ) as response:
                        if response.status < 500:
                            try:
                                data = await response.json()
                                return True, data, "OK"
                            except:
                                return True, {}, "OK"
                        
                        if attempt == max_retries - 1:
                            return False, {}, f"HTTP {response.status}"
            
            except asyncio.TimeoutError:
                if attempt == max_retries - 1:
                    self._record_failure()
                    return False, {}, "Timeout"
            
            except aiohttp.ClientError as e:
                if attempt == max_retries - 1:
                    self._record_failure()
                    return False, {}, f"Client error: {str(e)[:50]}"
            
            except Exception as e:
                self._record_failure()
                return False, {}, f"Error: {str(e)[:50]}"
            
            await asyncio.sleep(min(2 ** attempt, 10))
        
        return False, {}, "Max retries exceeded"
    
    def _sanitize_headers(self, headers: dict) -> dict:
        SENSITIVE_HEADERS = {
            "authorization", "cookie", "set-cookie",
            "x-api-key", "x-auth-token", "x-csrf-token"
        }
        
        return {
            k: v for k, v in headers.items()
            if k.lower() not in SENSITIVE_HEADERS
        }
    
    def _record_failure(self):
        self._failure_count += 1
        
        if self._failure_count >= self._failure_threshold:
            self._circuit_open = True
            logger.warning("API circuit breaker opened")
            
            asyncio.create_task(self._reset_circuit())
    
    async def _reset_circuit(self):
        await asyncio.sleep(self._circuit_timeout)
        self._circuit_open = False
        self._failure_count = 0
        logger.info("API circuit breaker reset")
    
    def reset_circuit(self):
        self._circuit_open = False
        self._failure_count = 0
    
    def is_circuit_open(self) -> bool:
        return self._circuit_open
    
    def safe_log_response(self, data: dict) -> dict:
        return redact_dict(data)
    
    def safe_log_error(self, error: str) -> str:
        return redact_text(error)


api_guard_service = APIGuardService()
