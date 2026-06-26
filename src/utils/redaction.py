import re
from typing import Any


SECRET_PATTERNS = [
    r"ghp_[a-zA-Z0-9]{32,}",
    r"gho_[a-zA-Z0-9]{32,}",
    r"glpat-[a-zA-Z0-9\-]{20,}",
]


def mask_secret(value: str) -> str:
    if not isinstance(value, str):
        return "***REDACTED***"
    if len(value) <= 8:
        return "***REDACTED***"
    return value[:4] + "***" + value[-4:]


def redact_text(text: str) -> str:
    if not text:
        return text
    
    redacted = text
    for pattern in SECRET_PATTERNS:
        try:
            redacted = re.sub(pattern, "[REDACTED]", redacted, flags=re.IGNORECASE)
        except re.error:
            continue
    
    return redacted


def redact_dict(data: dict, depth: int = 0) -> dict:
    if depth > 10:
        return {}
    
    if not isinstance(data, dict):
        return data
    
    SENSITIVE_KEYS = {
        "token", "password", "secret", "api_key", "apikey",
        "authorization", "auth", "bearer", "cookie", "set-cookie",
        "private_key", "access_token", "refresh_token"
    }
    
    result = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        if any(sk in key_lower for sk in SENSITIVE_KEYS):
            if isinstance(value, str):
                result[key] = mask_secret(value)
            else:
                result[key] = "***REDACTED***"
        elif isinstance(value, dict):
            result[key] = redact_dict(value, depth + 1)
        elif isinstance(value, list):
            result[key] = [
                redact_dict(item, depth + 1) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result


def safe_log_value(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, str):
        return redact_text(value)
    return redact_text(str(value))
