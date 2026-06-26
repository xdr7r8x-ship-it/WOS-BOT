import asyncio
import logging
from typing import Optional

from database import save_security_event, save_health_event
from src.utils.safe_json import mask_secrets

logger = logging.getLogger(__name__)


class AlertService:
    def __init__(self):
        self._alert_queue: asyncio.Queue = asyncio.Queue()
        self._log_channel = None
        self._admin_ids: list = []
        
    def set_log_channel(self, channel):
        self._log_channel = channel
        
    def set_admins(self, admin_ids: list):
        self._admin_ids = admin_ids
        
    async def send_alert(self, title: str, message: str, severity: str = "INFO", details: str = None):
        event_data = {
            "title": title,
            "message": mask_secrets(str(message)),
            "severity": severity,
            "details": mask_secrets(str(details)) if details else None
        }
        
        await self._alert_queue.put(event_data)
        
        if severity == "CRITICAL":
            save_security_event("ALERT", severity, mask_secrets(str(message)), mask_secrets(str(details)))
        else:
            save_health_event("ALERT", severity, mask_secrets(str(message)), mask_secrets(str(details)))
        
        if self._log_channel:
            try:
                import discord
                color = {
                    "INFO": 0x3498DB,
                    "WARNING": 0xF39C12,
                    "ERROR": 0xE74C3C,
                    "CRITICAL": 0x992222
                }.get(severity, 0x3498DB)
                
                embed = discord.Embed(
                    title=f"⚠️ {title}",
                    description=mask_secrets(str(message)),
                    color=color
                )
                
                await self._log_channel.send(embed=embed)
            except Exception as e:
                logger.error(f"Failed to send alert: {e}")
    
    async def send_startup_alert(self):
        await self.send_alert("Bot Started", "WOS-BOT Autopilot Operations System is now online", "INFO")
    
    async def send_shutdown_alert(self):
        await self.send_alert("Bot Stopped", "WOS-BOT is shutting down", "INFO")
    
    async def send_security_alert(self, message: str, details: str = None):
        await self.send_alert("Security Alert", message, "CRITICAL", details)
    
    async def send_update_alert(self, message: str):
        await self.send_alert("Update Alert", message, "INFO")
    
    async def send_backup_alert(self, success: bool, details: str = None):
        severity = "INFO" if success else "ERROR"
        message = "Backup completed successfully" if success else "Backup failed"
        await self.send_alert("Backup Alert", message, severity, details)
    
    async def process_alerts(self):
        while True:
            try:
                event = await self._alert_queue.get()
                await asyncio.sleep(0.1)
            except Exception:
                break


alert_service = AlertService()
