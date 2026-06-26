class CaptchaSolver:
    def __init__(self, api_key: str = None):
        if not api_key:
            raise ValueError("CaptchaSolver requires CAPTCHA_API_KEY environment variable")
        self.api_key = api_key

    async def solve(self, image_bytes: bytes) -> str:
        raise NotImplementedError("Captcha solving requires CAPTCHA_API_KEY")
