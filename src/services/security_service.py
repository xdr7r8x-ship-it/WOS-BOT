import re
from pathlib import Path
from typing import Optional

from database import save_security_event
from src.utils.safe_json import contains_secrets


SECRET_PATTERNS = [
    (r"TOKEN\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{20,}['\"]?", "BOT_TOKEN"),
    (r"password\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{8,}['\"]?", "PASSWORD"),
    (r"api[_-]?key\s*[:=]\s*['\"]?[A-Za-z0-9_\-\.]{20,}['\"]?", "API_KEY"),
    (r"ghp_[a-zA-Z0-9]{36}", "GITHUB_TOKEN"),
    (r"gho_[a-zA-Z0-9]{36}", "GITHUB_TOKEN"),
    (r"glpat-[a-zA-Z0-9\-]{20,}", "GITLAB_TOKEN"),
]


class SecurityService:
    def __init__(self):
        self._scan_results: list = []
        
    def scan_file(self, path: Path) -> dict:
        try:
            content = path.read_text(errors="ignore")
            matches = []
            
            for pattern, secret_type in SECRET_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    matches.append(secret_type)
            
            return {
                "path": str(path),
                "status": "FAIL" if matches else "PASS",
                "secrets_found": matches
            }
        except Exception as e:
            return {"path": str(path), "status": "ERROR", "error": str(e)}
    
    def scan_directory(self, directory: Path, extensions: list = None) -> list:
        if extensions is None:
            extensions = [".py", ".txt", ".md", ".json", ".yaml", ".yml", ".env"]
        
        results = []
        for ext in extensions:
            for file in directory.rglob(f"*{ext}"):
                result = self.scan_file(file)
                if result["status"] == "FAIL":
                    results.append(result)
                    save_security_event(
                        "SECRET_DETECTED",
                        "CRITICAL",
                        f"Potential secrets in {file}",
                        str(result.get("secrets_found"))
                    )
        
        return results
    
    def check_env_example(self) -> dict:
        env_example = Path(".env.example")
        if not env_example.exists():
            return {"status": "PASS", "message": ".env.example not present"}
        
        content = env_example.read_text(errors="ignore")
        
        if contains_secrets(content):
            return {"status": "FAIL", "message": ".env.example contains secrets"}
        
        return {"status": "PASS", "message": ".env.example is clean"}
    
    def check_backup_exclusion(self, backup_files: list) -> dict:
        excluded = []
        sensitive = [".env", "token", "secret", "key", "password"]
        
        for f in backup_files:
            name_lower = f.lower()
            if any(s in name_lower for s in sensitive):
                excluded.append(f)
        
        return {
            "status": "PASS" if not excluded else "WARN",
            "excluded_files": excluded
        }
    
    def scan_logs(self, log_dir: Path) -> dict:
        if not log_dir.exists():
            return {"status": "PASS", "message": "No logs to scan"}
        
        leaks = []
        for log_file in log_dir.glob("*.log"):
            try:
                content = log_file.read_text(errors="ignore")
                if contains_secrets(content):
                    leaks.append(str(log_file))
                    save_security_event(
                        "LOG_LEAK",
                        "CRITICAL",
                        f"Secrets potentially leaked in {log_file}"
                    )
            except Exception:
                pass
        
        return {
            "status": "FAIL" if leaks else "PASS",
            "files_with_leaks": leaks
        }
    
    def run_security_scan(self) -> dict:
        results = {
            "overall_status": "PASS",
            "checks": {}
        }
        
        results["checks"]["env_example"] = self.check_env_example()
        if results["checks"]["env_example"]["status"] == "FAIL":
            results["overall_status"] = "FAIL"
        
        return results


security_service = SecurityService()
