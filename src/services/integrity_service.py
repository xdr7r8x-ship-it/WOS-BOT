from pathlib import Path

from database import get_connection
from src.utils.config import get_config
from src.services.version_service import read_version


REQUIRED_FILES = [
    "VERSION",
    "main.py",
    "database.py",
    "requirements.txt",
]

REQUIRED_DIRS = [
    "src",
    "src/api",
    "src/services",
    "src/utils",
    "db",
]

REQUIRED_TABLES = [
    "guild_settings",
    "players",
    "gift_codes",
    "processed_codes",
    "redemption_history",
    "retry_jobs",
    "system_logs",
    "system_state",
    "service_status",
    "backups",
    "health_events",
    "service_locks",
    "prediction_events",
    "security_events",
    "migrations",
    "update_history",
]

REQUIRED_INDEXES = [
    "idx_players_guild_status",
    "idx_gift_codes_guild_status",
    "idx_redemption_history_code_player",
    "idx_retry_jobs_due",
]


class IntegrityService:
    def __init__(self):
        self.config = get_config()
    
    def check_required_files(self) -> dict:
        missing = []
        for fname in REQUIRED_FILES:
            if not Path(fname).exists():
                missing.append(fname)
        
        return {
            "status": "PASS" if not missing else "FAIL",
            "missing_files": missing
        }
    
    def check_required_directories(self) -> dict:
        missing = []
        for dname in REQUIRED_DIRS:
            if not Path(dname).is_dir():
                missing.append(dname)
        
        return {
            "status": "PASS" if not missing else "FAIL",
            "missing_directories": missing
        }
    
    def check_required_tables(self) -> dict:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            missing = [t for t in REQUIRED_TABLES if t not in existing]
            
            return {
                "status": "PASS" if not missing else "FAIL",
                "missing_tables": missing
            }
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def check_required_indexes(self) -> dict:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            existing = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            missing = [i for i in REQUIRED_INDEXES if i not in existing]
            
            return {
                "status": "PASS" if not missing else "FAIL",
                "missing_indexes": missing
            }
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def check_version_consistency(self) -> dict:
        version = read_version()
        if not version:
            return {"status": "FAIL", "message": "VERSION file missing or invalid"}
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM system_state WHERE key = 'version'")
            row = cursor.fetchone()
            conn.close()
            
            if row and row[0] != version:
                return {"status": "WARN", "message": "Version mismatch"}
            
            return {"status": "PASS", "version": version}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def run_integrity_check(self) -> dict:
        results = {
            "overall_status": "PASS",
            "checks": {}
        }
        
        checks = [
            ("required_files", self.check_required_files),
            ("required_directories", self.check_required_directories),
            ("required_tables", self.check_required_tables),
            ("required_indexes", self.check_required_indexes),
            ("version_consistency", self.check_version_consistency),
        ]
        
        for name, check_func in checks:
            result = check_func()
            results["checks"][name] = result
            if result.get("status") == "FAIL":
                results["overall_status"] = "FAIL"
            elif result.get("status") == "WARN" and results["overall_status"] != "FAIL":
                results["overall_status"] = "WARN"
        
        return results


integrity_service = IntegrityService()
