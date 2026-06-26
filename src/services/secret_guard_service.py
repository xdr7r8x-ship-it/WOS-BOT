import os
import re
from pathlib import Path
from typing import Optional

from database import save_security_event, save_security_incident
from src.utils.redaction import redact_text
from src.utils.security import sanitize_filename


SENSITIVE_PATTERNS = [
    r"DISCORD_BOT_TOKEN",
    r"Authorization",
    r"Bearer\s+[a-zA-Z0-9_\-\.]+",
    r"api[_-]?key",
    r"ghp_[a-zA-Z0-9]{36}",
    r"gho_[a-zA-Z0-9]{36}",
    r"glpat-[a-zA-Z0-9\-]{20,}",
]


class SecretGuardService:
    def __init__(self):
        self._sensitive_files = {".env", ".env.local", ".env.production"}
        
    def scan_file_for_secrets(self, file_path: Path) -> tuple[bool, list]:
        try:
            content = file_path.read_text(errors="ignore")
            found = []
            
            for pattern in SENSITIVE_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    found.append(pattern)
            
            return len(found) > 0, found
        except Exception:
            return False, []
    
    def scan_content_for_secrets(self, content: str) -> bool:
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                return True
        return False
    
    def check_backup_for_secrets(self, backup_path: Path) -> tuple[bool, list]:
        violations = []
        
        for sensitive_file in self._sensitive_files:
            env_file = backup_path / sensitive_file
            if env_file.exists():
                violations.append(sensitive_file)
        
        return len(violations) > 0, violations
    
    def check_env_example(self) -> tuple[bool, str]:
        env_example = Path(".env.example")
        
        if not env_example.exists():
            return True, "File not found"
        
        content = env_example.read_text(errors="ignore")
        
        if self.scan_content_for_secrets(content):
            return False, "Contains secrets"
        
        return True, "OK"
    
    def redact_for_log(self, text: str) -> str:
        return redact_text(text)
    
    def is_safe_to_backup(self, file_path: Path) -> bool:
        filename = file_path.name
        
        for sensitive in self._sensitive_files:
            if filename == sensitive or filename.startswith(".env"):
                return False
        
        return True
    
    def record_secret_leak(self, location: str, details: str):
        save_security_event(
            event_type="SECRET_LEAK",
            severity="CRITICAL",
            message=f"Potential secret leak in {location}",
            details=details
        )
        
        save_security_incident(
            guild_id=None,
            incident_type="SECRET_LEAK",
            severity="CRITICAL",
            message=f"Potential secret leak in {location}",
            action_taken="Logged and alerted"
        )


secret_guard_service = SecretGuardService()
