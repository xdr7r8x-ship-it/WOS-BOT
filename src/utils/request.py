import asyncio
import random
import time
from typing import Optional, Callable

import aiohttp

from .errors import ErrorType


class RequestClient:
    def __init__(
        self,
        base_url: str = "https://api.whiteout.io",
        timeout: int = 15,
        max_retries: int = 5,
    ):
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self._session: Optional[aiohttp.ClientSession] = None
        self._jitter = (0.5, 2.0)
        self._backoff_base = 2

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self.timeout)
        return self._session

    def _calculate_backoff(self, attempt: int) -> float:
        base = self._backoff_base ** attempt
        jitter = random.uniform(*self._jitter)
        return min(base * jitter, 45)

    async def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> tuple[dict, ErrorType]:
        session = await self._get_session()
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries):
            try:
                async with session.request(
                    method, url, params=params, json=json_data, headers=headers
                ) as resp:
                    if resp.status == 429:
                        return {"code": 429, "msg": "Rate limited"}, ErrorType.RATE_LIMIT
                    
                    if resp.status >= 500:
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(self._calculate_backoff(attempt))
                            continue
                        return {"code": resp.status, "msg": "Server error"}, ErrorType.TEMPORARY_API_ERROR
                    
                    try:
                        data = await resp.json()
                        return data, ErrorType.NETWORK_ERROR if data.get("code") < 0 else None
                    except:
                        return {"code": resp.status, "msg": await resp.text()}, None

            except asyncio.TimeoutError:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self._calculate_backoff(attempt))
                    continue
                return {"code": -1, "msg": "Request timeout"}, ErrorType.TIMEOUT

            except aiohttp.ClientError as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self._calculate_backoff(attempt))
                    continue
                return {"code": -1, "msg": str(e)}, ErrorType.NETWORK_ERROR

            except Exception as e:
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self._calculate_backoff(attempt))
                    continue
                return {"code": -1, "msg": str(e)}, ErrorType.UNKNOWN_ERROR

        return {"code": -1, "msg": "Max retries exceeded"}, ErrorType.UNKNOWN_ERROR

    async def get(self, endpoint: str, params: Optional[dict] = None) -> tuple[dict, ErrorType]:
        return await self.request("GET", endpoint, params=params)

    async def post(self, endpoint: str, json_data: Optional[dict] = None) -> tuple[dict, ErrorType]:
        return await self.request("POST", endpoint, json_data=json_data)

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
