import re
import html


PLAYER_ID_PATTERN = re.compile(r"^\d{6,15}$")

GIFT_CODE_PATTERN = re.compile(r"^[A-Z0-9]{4,20}$")

DANGEROUS_PATTERNS = [
    r"<script",
    r"javascript:",
    r"on\w+\s*=",
    r"@everyone",
    r"@here",
]


def sanitize_player_id(player_id: str) -> tuple[bool, str]:
    if not player_id:
        return False, "EMPTY"
    
    player_id = player_id.strip()
    
    if PLAYER_ID_PATTERN.match(player_id):
        return True, player_id
    
    return False, "INVALID"


def sanitize_gift_code(code: str) -> str:
    if not code:
        return ""
    
    code = code.strip().upper()
    code = code.replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    
    code = re.sub(r"[^A-Z0-9]", "", code)
    
    return code


def is_safe_player_id(player_id: str) -> bool:
    if not player_id:
        return False
    
    if not PLAYER_ID_PATTERN.match(player_id.strip()):
        return False
    
    if any(char.isalpha() for char in player_id):
        return False
    
    return True


def is_safe_gift_code(code: str) -> bool:
    if not code:
        return False
    
    normalized = sanitize_gift_code(code)
    
    if len(normalized) < 4 or len(normalized) > 20:
        return False
    
    if not GIFT_CODE_PATTERN.match(normalized):
        return False
    
    if not any(char.isdigit() for char in normalized):
        return False
    
    return True


def contains_dangerous_pattern(text: str) -> bool:
    if not text:
        return False
    
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False


def clean_mentions(text: str) -> str:
    text = re.sub(r"<@!?\d+>", "", text)
    text = re.sub(r"@everyone", "", text, flags=re.IGNORECASE)
    text = re.sub(r"@here", "", text, flags=re.IGNORECASE)
    return text


def escape_for_embed(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"@everyone", "@\u200Beveryone", text, flags=re.IGNORECASE)
    text = re.sub(r"@here", "@\u200Bhere", text, flags=re.IGNORECASE)
    text = re.sub(r"<@!?(\d+)>", "@\u200Buser", text)
    return text


def is_valid_length(text: str, max_length: int = 2000) -> bool:
    return len(text) <= max_length


def sanitize_for_storage(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text[:2000]
