import random
import string


class CaptchaSolver:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    async def solve(self, image_bytes: bytes) -> str:
        if self.api_key:
            return await self._solve_with_api(image_bytes)
        return await self._solve_mock(image_bytes)

    async def _solve_with_api(self, image_bytes: bytes) -> str:
        return await self._solve_mock(image_bytes)

    async def _solve_mock(self, image_bytes: bytes) -> str:
        chars = string.ascii_lowercase + string.digits
        return "".join(random.choices(chars, k=4))
