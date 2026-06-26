from src.utils.sanitizer import (
    sanitize_player_id,
    sanitize_gift_code,
    is_safe_player_id,
    is_safe_gift_code,
    contains_dangerous_pattern,
    clean_mentions,
    escape_for_embed,
    is_valid_length,
    sanitize_for_storage
)
from src.utils.security import hash_input, is_malicious_content, truncate_for_log


class InputGuardService:
    def __init__(self):
        self.max_code_length = 100
        self.max_player_id_length = 20
        
    def validate_player_id(self, player_id: str) -> tuple[bool, str]:
        if not player_id:
            return False, "EMPTY"
        
        if len(player_id) > self.max_player_id_length:
            return False, "TOO_LONG"
        
        if is_malicious_content(player_id):
            return False, "MALICIOUS"
        
        return sanitize_player_id(player_id)
    
    def validate_gift_code(self, code: str) -> tuple[bool, str]:
        if not code:
            return False, "EMPTY"
        
        if len(code) > self.max_code_length:
            return False, "TOO_LONG"
        
        if is_malicious_content(code):
            return False, "MALICIOUS"
        
        normalized = sanitize_gift_code(code)
        
        if not is_safe_gift_code(normalized):
            return False, "INVALID"
        
        return True, normalized
    
    def sanitize_and_validate_player_id(self, player_id: str) -> tuple[bool, str]:
        valid, result = self.validate_player_id(player_id)
        
        if valid:
            return True, result
        
        return False, "INVALID"
    
    def sanitize_and_validate_gift_code(self, code: str) -> tuple[bool, str]:
        valid, result = self.validate_gift_code(code)
        
        if valid:
            return True, result
        
        return False, "INVALID"
    
    def check_dangerous_input(self, text: str) -> tuple[bool, str]:
        if contains_dangerous_pattern(text):
            return True, "DANGEROUS_PATTERNS"
        
        if is_malicious_content(text):
            return True, "MALICIOUS"
        
        return False, "SAFE"
    
    def get_input_hash(self, text: str) -> str:
        return hash_input(text)
    
    def safe_log_player_id(self, player_id: str) -> str:
        if len(player_id) <= 4:
            return "***REDACTED***"
        return player_id[:2] + "***" + player_id[-2:]
    
    def safe_log_gift_code(self, code: str) -> str:
        if len(code) <= 4:
            return "***REDACTED***"
        return code[:2] + "***" + code[-2:]
    
    def prepare_for_storage(self, text: str) -> str:
        return sanitize_for_storage(text)
    
    def prepare_for_embed(self, text: str) -> str:
        return escape_for_embed(text)


input_guard_service = InputGuardService()
