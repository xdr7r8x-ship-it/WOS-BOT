import re


PLAYER_ID_PATTERN = re.compile(r"^\d{6,15}$")

GIFT_CODE_PATTERN = re.compile(r"[A-Z0-9]{4,20}")


def validate_player_id(player_id: str) -> bool:
    if not player_id:
        return False
    return bool(PLAYER_ID_PATTERN.match(player_id.strip()))


def validate_gift_code(code: str) -> bool:
    if not code:
        return False
    normalized = code.strip().upper().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
    if not GIFT_CODE_PATTERN.fullmatch(normalized):
        return False
    if not any(c.isdigit() for c in normalized):
        return False
    return True


def normalize_gift_code(code: str) -> str:
    if not code:
        return ""
    return code.strip().upper().replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")


def extract_codes_from_text(text: str) -> list[str]:
    if not text:
        return []
    matches = GIFT_CODE_PATTERN.findall(text.upper())
    codes = []
    for c in matches:
        normalized = normalize_gift_code(c)
        if validate_gift_code(normalized) and normalized not in codes:
            codes.append(normalized)
    return codes


def is_valid_registration_input(text: str) -> tuple[bool, str]:
    text = text.strip()
    
    if not text:
        return False, "EMPTY"
    
    if PLAYER_ID_PATTERN.match(text):
        return True, "VALID"
    
    return False, "INVALID"
