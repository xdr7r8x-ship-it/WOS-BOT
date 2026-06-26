import os
import hashlib
from typing import Optional

from src.utils.config import get_config


def hash_input(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def is_safe_path(path: str, allowed_dir: str) -> bool:
    abs_allowed = os.path.abspath(allowed_dir)
    abs_path = os.path.abspath(os.path.join(allowed_dir, path))
    return abs_path.startswith(abs_allowed)


def check_rate_limit_key(user_id: str, action: str, window: int = 60) -> str:
    return f"{user_id}:{action}"


def sanitize_filename(filename: str) -> str:
    keep = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    return "".join(c if c in keep else "_" for c in filename)


def is_malicious_content(text: str) -> bool:
    dangerous_patterns = [
        "\x00",
        "\r\n{3,}",
        "\x1b[",
        "{{",
        "}}",
    ]
    
    for pattern in dangerous_patterns:
        if pattern in text:
            return True
    
    return False


def truncate_for_log(text: str, max_length: int = 500) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "...[TRUNCATED]"
