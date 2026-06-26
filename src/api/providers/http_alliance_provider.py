import os
import logging
import asyncio
import time
from typing import Optional
from src.api import AllianceProviderBase

logger = logging.getLogger(__name__)


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = 0
        self.state = "CLOSED"
    
    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.failure_threshold:
            self.state = "OPEN"
    
    def is_open(self) -> bool:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
                return False
            return True
        return False


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = []
    
    def is_allowed(self) -> bool:
        now = time.time()
        self.requests = [r for r in self.requests if now - r < self.window_seconds]
        if len(self.requests) >= self.max_requests:
            return False
        self.requests.append(now)
        return True
    
    def get_remaining(self) -> int:
        now = time.time()
        self.requests = [r for r in self.requests if now - r < self.window_seconds]
        return max(0, self.max_requests - len(self.requests))


class HttpAllianceProvider(AllianceProviderBase):
    
    def __init__(self):
        self.base_url = os.getenv("ALLIANCE_API_BASE_URL", "")
        self.api_key = os.getenv("ALLIANCE_API_KEY", "")
        self.timeout = int(os.getenv("ALLIANCE_API_TIMEOUT_SECONDS", "15"))
        self.max_retries = int(os.getenv("ALLIANCE_API_MAX_RETRIES", "3"))
        self.rate_limit = int(os.getenv("ALLIANCE_API_RATE_LIMIT_PER_MINUTE", "30"))
        
        self.circuit_breaker = CircuitBreaker()
        self.rate_limiter = RateLimiter(self.rate_limit, 60)
        
        self._health_cache = None
        self._health_cache_time = 0
        self._last_error = None
    
    @property
    def provider_name(self) -> str:
        return "HTTP"
    
    @property
    def is_enabled(self) -> bool:
        return bool(self.base_url)
    
    async def health_check(self) -> dict:
        if self._health_cache and (time.time() - self._health_cache_time) < 30:
            return self._health_cache
        
        result = {
            "status": "UNKNOWN",
            "provider": self.provider_name,
            "enabled": self.is_enabled,
            "base_url_configured": bool(self.base_url),
            "circuit_breaker": self.circuit_breaker.state,
            "rate_limit_remaining": self.rate_limiter.get_remaining(),
            "last_error": self._last_error,
        }
        
        if not self.is_enabled:
            result["status"] = "DISABLED"
            result["message"] = "API base URL not configured"
        elif self.circuit_breaker.is_open():
            result["status"] = "OPEN"
            result["message"] = "Circuit breaker open"
        elif not self.rate_limiter.is_allowed():
            result["status"] = "RATE_LIMITED"
            result["message"] = "Rate limit exceeded"
        else:
            result["status"] = "HEALTHY"
            result["message"] = "API accessible"
        
        self._health_cache = result
        self._health_cache_time = time.time()
        return result
    
    async def fetch_alliance(self, alliance_tag: str) -> Optional[dict]:
        if self.circuit_breaker.is_open():
            logger.warning(f"Circuit breaker open, skipping fetch_alliance for {alliance_tag}")
            return None
        
        if not self.rate_limiter.is_allowed():
            logger.warning(f"Rate limit exceeded for fetch_alliance")
            return None
        
        try:
            async with asyncio.timeout(self.timeout):
                return await self._do_fetch_alliance(alliance_tag)
        except asyncio.TimeoutError:
            self.circuit_breaker.record_failure()
            self._last_error = f"Timeout fetching alliance {alliance_tag}"
            logger.error(self._last_error)
            return None
        except Exception as e:
            self.circuit_breaker.record_failure()
            self._last_error = f"Error fetching alliance: {type(e).__name__}"
            logger.error(self._last_error)
            return None
    
    async def _do_fetch_alliance(self, alliance_tag: str) -> Optional[dict]:
        import aiohttp
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key[:8]}***"
        
        url = f"{self.base_url.rstrip('/')}/alliances/{alliance_tag}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status == 404:
                    return None
                if resp.status != 200:
                    self.circuit_breaker.record_failure()
                    self._last_error = f"HTTP {resp.status}"
                    return None
                
                self.circuit_breaker.record_success()
                data = await resp.json()
                
                return {
                    "alliance_tag": data.get("tag", alliance_tag),
                    "alliance_name": data.get("name", ""),
                    "external_id": data.get("id"),
                }
    
    async def fetch_alliance_members(self, alliance_tag: str) -> list[dict]:
        if self.circuit_breaker.is_open():
            return []
        
        if not self.rate_limiter.is_allowed():
            return []
        
        try:
            async with asyncio.timeout(self.timeout):
                return await self._do_fetch_members(alliance_tag)
        except:
            self.circuit_breaker.record_failure()
            self._last_error = f"Timeout fetching members for {alliance_tag}"
            return []
    
    async def _do_fetch_members(self, alliance_tag: str) -> list[dict]:
        import aiohttp
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key[:8]}***"
        
        url = f"{self.base_url.rstrip('/')}/alliances/{alliance_tag}/members"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    self.circuit_breaker.record_failure()
                    return []
                
                self.circuit_breaker.record_success()
                data = await resp.json()
                
                members = []
                for member in data.get("members", []):
                    members.append({
                        "player_id": str(member.get("player_id", "")),
                        "rank": member.get("rank", "R1"),
                        "alliance_tag": alliance_tag,
                        "alliance_name": member.get("alliance_name", ""),
                        "last_seen_at": member.get("last_online", ""),
                    })
                
                return members
    
    async def fetch_player(self, player_id: str) -> Optional[dict]:
        if self.circuit_breaker.is_open():
            return None
        
        if not self.rate_limiter.is_allowed():
            return None
        
        try:
            async with asyncio.timeout(self.timeout):
                return await self._do_fetch_player(player_id)
        except:
            return None
    
    async def _do_fetch_player(self, player_id: str) -> Optional[dict]:
        import aiohttp
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key[:8]}***"
        
        url = f"{self.base_url.rstrip('/')}/players/{player_id}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=self.timeout) as resp:
                if resp.status != 200:
                    return None
                
                data = await resp.json()
                
                return {
                    "player_id": str(data.get("player_id", player_id)),
                    "rank": data.get("rank", "R1"),
                    "alliance_tag": data.get("alliance_tag", ""),
                    "alliance_name": data.get("alliance_name", ""),
                }
