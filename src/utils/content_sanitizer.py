import re
import logging

logger = logging.getLogger(__name__)

DANGEROUS_PATTERNS = [
    (r"@everyone", "Mention injection"),
    (r"@here", "Mention injection"),
    (r"<@!?\d+>", "User mention"),
    (r"<#\d+>", "Channel mention"),
    (r"<@&\d+>", "Role mention"),
    (r"@role:\d+", "Role mention"),
    (r"(?i)token[:=]\s*[a-zA-Z0-9_\-.]+", "Token pattern"),
    (r"(?i)api[_-]?key[:=]\s*[a-zA-Z0-9_\-.]+", "API key pattern"),
    (r"(?i)bearer\s+[a-zA-Z0-9_\-.]+", "Bearer token"),
    (r"(?i)authorization[:=]", "Authorization header"),
    (r"(?i)password[:=]\s*\S+", "Password pattern"),
    (r"(?i)secret[:=]\s*\S+", "Secret pattern"),
    (r"https?://[^\s]+", "URL (restricted)"),
    (r"```[\s\S]*```", "Code block"),
    (r"```", "Code block marker"),
    (r"`[^`]+`", "Inline code"),
]

CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f-\x9f]")

ALLOWED_MARKDOWN = re.compile(r"^[\w\s\u0600-\u06ff\u0750-\u077f\ufb50-\ufdff\ufe70-\ufefe\uff00-\uffef\u0980-\u09ff\u0a80-\u0aff\u0b80-\u0bff\u0c80-\u0cff\u0d80-\u0dff\.\,\!\?\:\;\-\(\)\[\]\{\}\_\+\=\*\/\|\~\@\#\$\%\^\&\'\\\"\n\r\t ]+$")


class SanitizationResult:
    def __init__(self, is_valid: bool, sanitized_text: str = "", error: str = ""):
        self.is_valid = is_valid
        self.sanitized_text = sanitized_text
        self.error = error


def sanitize_content(text: str, max_length: int = 500, allow_links: bool = False) -> SanitizationResult:
    if not text or not isinstance(text, str):
        return SanitizationResult(False, "", "Text cannot be empty")
    
    text = text.strip()
    
    if len(text) > max_length:
        return SanitizationResult(False, "", f"Text exceeds maximum length of {max_length} characters")
    
    if not text:
        return SanitizationResult(False, "", "Text cannot be empty")
    
    if CONTROL_CHARS.search(text):
        text = CONTROL_CHARS.sub("", text)
    
    for pattern, reason in DANGEROUS_PATTERNS:
        if not allow_links and "URL" in reason:
            continue
        if re.search(pattern, text, re.IGNORECASE):
            if "Code block" in reason:
                text = re.sub(pattern, "[code]", text)
            else:
                return SanitizationResult(False, "", f"Text contains prohibited content: {reason}")
    
    if re.search(r"discord[.\-]?token", text, re.IGNORECASE):
        return SanitizationResult(False, "", "Text contains potential Discord token")
    
    if re.search(r"\.env", text, re.IGNORECASE):
        return SanitizationResult(False, "", "Text contains potential .env reference")
    
    return SanitizationResult(True, text, "")


def validate_no_mentions(text: str) -> bool:
    mention_patterns = [
        r"@everyone",
        r"@here",
        r"<@!?\d+>",
        r"<#\d+>",
        r"<@&\d+>",
    ]
    
    for pattern in mention_patterns:
        if re.search(pattern, text):
            return False
    
    return True


def sanitize_for_embed(text: str, max_length: int = 1024) -> str:
    result = sanitize_content(text, max_length, allow_links=False)
    if result.is_valid:
        return result.sanitized_text
    return "[Content sanitized]"
