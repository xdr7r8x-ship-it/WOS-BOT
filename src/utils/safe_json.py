import json
import re
from typing import Any, Optional


SECRETS_PATTERNS = [
    r"token['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9_\-\.]{20,}['\"]?",
    r"password['\"]?\s*[:=]\s*['\"]?[^'\"\s]{8,}['\"]?",
    r"api[_-]?key['\"]?\s*[:=]\s*['\"]?[a-zA-Z0-9_\-\.]{20,}['\"]?",
    r"secret['\"]?\s*[:=]\s*['\"]?[^'\"\s]{8,}['\"]?",
    r"BOT[_\s]+[a-zA-Z0-9_\-\.]{50,}",
    r"ghp_[a-zA-Z0-9]{36}",
    r"gho_[a-zA-Z0-9]{36}",
    r"glpat-[a-zA-Z0-9\-]{20,}",
]

SECRETS_REGEX = [re.compile(p, re.IGNORECASE) for p in SECRETS_PATTERNS]


def mask_secrets(text: str) -> str:
    masked = text
    for pattern in SECRETS_REGEX:
        masked = pattern.sub("[REDACTED]", masked)
    return masked


def load_json(path: str) -> Optional[dict]:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def save_json(path: str, data: dict) -> bool:
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def read_json_safe(path: str, default: Any = None) -> Any:
    result = load_json(path)
    return result if result is not None else default


def contains_secrets(text: str) -> bool:
    for pattern in SECRETS_REGEX:
        if pattern.search(text):
            return True
    return False


def sanitize_for_log(text: str) -> str:
    return mask_secrets(str(text))
