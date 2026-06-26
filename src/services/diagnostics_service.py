from pathlib import Path
from typing import Optional

from src.utils.config import get_config
from src.utils.system import get_python_version, get_disk_usage_percent, get_memory_usage_percent
from database import get_connection


REQUIRED_PACKAGES = ["discord", "aiohttp", "psutil"]


class DiagnosticsService:
    def __init__(self):
        self.config = get_config()
        
    def check_python_version(self) -> dict:
        version = get_python_version()
        major, minor = version.split(".")[:2]
        return {
            "status": "PASS" if int(major) >= 3 and int(minor) >= 8 else "FAIL",
            "version": version
        }
    
    def check_package(self, package: str) -> dict:
        try:
            if package == "discord":
                import discord as d
                version = d.__version__
            elif package == "aiohttp":
                import aiohttp
                version = aiohttp.__version__
            elif package == "psutil":
                import psutil
                version = psutil.__version__
            else:
                __import__(package)
                import importlib
                mod = importlib.import_module(package)
                version = getattr(mod, "__version__", "unknown")
            
            return {"status": "PASS", "version": version}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def check_env_file(self) -> dict:
        env_path = Path(".env")
        if not env_path.exists():
            return {"status": "WARN", "message": ".env file missing"}
        
        return {"status": "PASS", "message": ".env exists"}
    
    def check_bot_token(self) -> dict:
        if not self.config.DISCORD_BOT_TOKEN:
            return {"status": "FAIL", "message": "DISCORD_BOT_TOKEN not set"}
        return {"status": "PASS", "message": "Token configured"}
    
    def check_database(self) -> dict:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return {"status": "PASS", "message": "Database reachable"}
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def check_wal_mode(self) -> dict:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("PRAGMA journal_mode")
            mode = cursor.fetchone()[0]
            conn.close()
            return {
                "status": "PASS" if mode.upper() == "WAL" else "FAIL",
                "mode": mode
            }
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def check_required_tables(self) -> dict:
        tables = [
            "guild_settings", "players", "gift_codes", "processed_codes",
            "redemption_history", "retry_jobs", "system_logs",
            "system_state", "service_status", "backups"
        ]
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            existing = {row[0] for row in cursor.fetchall()}
            conn.close()
            
            missing = [t for t in tables if t not in existing]
            return {
                "status": "PASS" if not missing else "FAIL",
                "missing_tables": missing
            }
        except Exception as e:
            return {"status": "FAIL", "error": str(e)}
    
    def check_directories(self) -> dict:
        dirs = {
            "backup_dir": Path(self.config.BACKUP_DIR),
            "logs_dir": Path(self.config.LOGS_DIR),
            "db_dir": Path(self.config.DB_DIR)
        }
        results = {}
        all_pass = True
        for name, path in dirs.items():
            exists = path.exists()
            writable = path.exists() and self._is_writable(path)
            results[name] = {
                "exists": exists,
                "writable": writable,
                "status": "PASS" if (exists and writable) else "FAIL"
            }
            if not (exists and writable):
                all_pass = False
        
        return {"status": "PASS" if all_pass else "WARN", "directories": results}
    
    def _is_writable(self, path: Path) -> bool:
        try:
            test = path / ".test"
            test.touch()
            test.unlink()
            return True
        except Exception:
            return False
    
    def check_version_file(self) -> dict:
        version_path = Path("VERSION")
        if not version_path.exists():
            return {"status": "FAIL", "message": "VERSION file missing"}
        return {"status": "PASS", "message": "VERSION exists"}
    
    def check_disk_space(self) -> dict:
        percent = get_disk_usage_percent("/")
        return {
            "status": "PASS" if percent < 90 else "WARN",
            "percent": percent
        }
    
    def check_memory(self) -> dict:
        percent = get_memory_usage_percent()
        return {
            "status": "PASS" if percent < 90 else "WARN",
            "percent": percent
        }
    
    async def run_full_diagnostics(self) -> dict:
        results = {
            "overall_status": "PASS",
            "checks": {}
        }
        
        checks = [
            ("python_version", self.check_python_version),
            ("bot_token", self.check_bot_token),
            ("database", self.check_database),
            ("wal_mode", self.check_wal_mode),
            ("required_tables", self.check_required_tables),
            ("directories", self.check_directories),
            ("version_file", self.check_version_file),
            ("disk_space", self.check_disk_space),
            ("memory", self.check_memory),
        ]
        
        for name, check_func in checks:
            try:
                result = check_func()
                results["checks"][name] = result
                if result.get("status") == "FAIL":
                    results["overall_status"] = "FAIL"
                elif result.get("status") == "WARN" and results["overall_status"] != "FAIL":
                    results["overall_status"] = "WARN"
            except Exception as e:
                results["checks"][name] = {"status": "FAIL", "error": str(e)}
                results["overall_status"] = "FAIL"
        
        return results


diagnostics_service = DiagnosticsService()
