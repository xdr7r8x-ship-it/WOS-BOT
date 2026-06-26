from typing import Optional
from src.api import AllianceProviderBase


class ManualAllianceProvider(AllianceProviderBase):
    
    @property
    def provider_name(self) -> str:
        return "MANUAL"
    
    @property
    def is_enabled(self) -> bool:
        return True
    
    async def health_check(self) -> dict:
        return {
            "status": "HEALTHY",
            "provider": self.provider_name,
            "enabled": True,
            "message": "Manual mode active. No API required."
        }
    
    async def fetch_alliance(self, alliance_tag: str) -> Optional[dict]:
        return None
    
    async def fetch_alliance_members(self, alliance_tag: str) -> list[dict]:
        return []
    
    async def fetch_player(self, player_id: str) -> Optional[dict]:
        return None
