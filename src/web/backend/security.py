import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
import re


def hash_sensitive(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()[:16]


def sanitize_for_log(value: str) -> str:
    patterns = [
        (r'(token["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r'\1[REDACTED]'),
        (r'(api[_-]?key["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r'\1[REDACTED]'),
        (r'(password["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r'\1[REDACTED]'),
        (r'(secret["\']?\s*[:=]\s*["\']?)([^"\'&\s]+)', r'\1[REDACTED]'),
        (r'(WOS_API_KEY|DISCORD_BOT_TOKEN|ALLIANCE_API_KEY)[^"\']*["\']?\s*[:=]\s*["\']?([^"\'&\s]+)', r'\1=[REDACTED]'),
    ]
    for pattern, replacement in patterns:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    return value


def generate_session_id() -> str:
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, secret: str) -> bool:
    expected = hashlib.sha256(f"{secret}".encode()).hexdigest()[:32]
    return secrets.compare_digest(token, expected)


def rate_limit_key(identifier: str, endpoint: str) -> str:
    return f"rl:{hashlib.md5(f'{identifier}:{endpoint}'.encode()).hexdigest()[:8]}"


class RateLimiter:
    def __init__(self, max_requests: int = 120, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: Dict[str, list] = {}

    def is_allowed(self, key: str) -> tuple[bool, int]:
        now = datetime.utcnow()
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key] = [
            ts for ts in self._requests[key]
            if (now - ts).total_seconds() < self.window_seconds
        ]
        if len(self._requests[key]) >= self.max_requests:
            return False, self.window_seconds
        self._requests[key].append(now)
        return True, 0


rate_limiter = RateLimiter()
