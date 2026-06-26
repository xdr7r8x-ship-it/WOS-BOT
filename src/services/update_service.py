import asyncio
from typing import Optional

from src.utils.config import get_config
from src.services.version_service import read_version, compare_versions, get_version_type
from src.services.backup_service import backup_service
from src.services.rollback_service import rollback_service
from database import save_update_history


class UpdateService:
    def __init__(self):
        self.config = get_config()
        self.current_version = read_version()
        self.update_available = False
        self.latest_version = None
        
    async def check_for_updates(self) -> tuple[bool, Optional[str]]:
        if not self.config.UPDATES_ENABLED:
            return False, "Updates disabled"
        
        if not self.config.UPDATE_CHECK_URL:
            return False, "No update URL configured"
        
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                url = f"{self.config.UPDATE_CHECK_URL}?channel={self.config.UPDATE_CHANNEL}"
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        import json
                        data = await resp.json()
                        self.latest_version = data.get("version")
                        
                        if self.latest_version and self.current_version:
                            if compare_versions(self.latest_version, self.current_version) > 0:
                                self.update_available = True
                                return True, self.latest_version
        except Exception:
            pass
        
        return False, None
    
    def create_update_plan(self) -> dict:
        if not self.latest_version or not self.current_version:
            return {"can_update": False, "reason": "Version info missing"}
        
        update_type = get_version_type(self.current_version, self.latest_version)
        
        can_update = True
        reason = None
        
        if update_type == "MAJOR" and not self.config.UPDATE_AUTO_MAJOR:
            can_update = False
            reason = "Major update requires manual approval"
        elif update_type == "MINOR" and not self.config.UPDATE_AUTO_MINOR:
            can_update = False
            reason = "Minor update requires manual approval"
        elif update_type == "PATCH" and not self.config.UPDATE_AUTO_PATCH:
            can_update = False
            reason = "Patch update disabled"
        
        return {
            "can_update": can_update,
            "current_version": self.current_version,
            "latest_version": self.latest_version,
            "update_type": update_type,
            "reason": reason,
        }
    
    async def apply_update(self) -> tuple[bool, str]:
        plan = self.create_update_plan()
        
        if not plan["can_update"]:
            return False, plan.get("reason", "Cannot update")
        
        success, path = backup_service.create_backup()
        if not success:
            return False, f"Backup failed: {path}"
        
        save_update_history(
            self.current_version,
            self.latest_version,
            "IN_PROGRESS"
        )
        
        try:
            return True, f"Update plan created. Latest version: {self.latest_version}"
        except Exception as e:
            rollback_service.restore_latest_backup()
            save_update_history(
                self.current_version,
                self.latest_version,
                "FAILED",
                str(e)
            )
            return False, str(e)


update_service = UpdateService()
