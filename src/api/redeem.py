import asyncio
import hashlib
import random
import time
from typing import Optional

import aiohttp

from ..utils.errors import ErrorType


class WhiteoutAPI:
    BASE_URL = "https://api.whiteout.io"
    APP_VERSION = "3.2.2"
    BUNDLE_ID = "com.babeltime.pap.global"
    API_KEY = "s3cr3tk3y"
    DEVICE_ID = "auto_" + "".join(random.choices("0123456789abcdef", k=16))

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=15)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    def _generate_sign(self, params: dict) -> str:
        sorted_keys = sorted(params.keys())
        sign_str = "&".join(f"{k}={params[k]}" for k in sorted_keys)
        sign_str += self.API_KEY
        return hashlib.md5(sign_str.encode()).hexdigest()

    def _get_common_params(self) -> dict:
        return {
            "timestamp": str(int(time.time())),
            "random_str": "".join(random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=6)),
            "device_id": self.DEVICE_ID,
            "app_version": self.APP_VERSION,
            "bundle_id": self.BUNDLE_ID,
        }

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        data: Optional[dict] = None,
    ) -> tuple[dict, Optional[ErrorType]]:
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"

        common = self._get_common_params()
        if params:
            common.update(params)
        params = common

        sign = self._generate_sign(params)
        params["sign"] = sign

        headers = {
            "Content-Type": "application/json",
            "User-Agent": "okhttp/3.10.0.1",
        }

        try:
            if method.upper() == "GET":
                async with session.get(url, params=params, headers=headers) as resp:
                    if resp.status == 429:
                        return {"code": 429}, ErrorType.RATE_LIMIT
                    if resp.status >= 500:
                        return {"code": resp.status}, ErrorType.TEMPORARY_API_ERROR
                    return await resp.json(), None
            else:
                async with session.post(url, params=params, json=data, headers=headers) as resp:
                    if resp.status == 429:
                        return {"code": 429}, ErrorType.RATE_LIMIT
                    if resp.status >= 500:
                        return {"code": resp.status}, ErrorType.TEMPORARY_API_ERROR
                    return await resp.json(), None

        except asyncio.TimeoutError:
            return {"code": -1, "msg": "Timeout"}, ErrorType.TIMEOUT
        except aiohttp.ClientError as e:
            return {"code": -1, "msg": str(e)}, ErrorType.NETWORK_ERROR
        except Exception as e:
            return {"code": -1, "msg": str(e)}, ErrorType.UNKNOWN_ERROR

        return {"code": -1, "msg": "Unknown error"}, ErrorType.UNKNOWN_ERROR

    async def redeem(
        self, player_id: str, giftcode: str
    ) -> tuple[dict, Optional[ErrorType]]:
        data = {
            "fid": player_id,
            "giftcode": giftcode,
        }
        return await self._request("POST", "/gift/redeem", data=data)

    async def check_status(
        self, player_id: str, giftcode: str
    ) -> tuple[dict, Optional[ErrorType]]:
        return await self._request(
            "GET", "/gift/status", params={"fid": player_id, "giftcode": giftcode}
        )

    async def close(self):
        if self._session:
            await self._session.close()
            self._session = None
