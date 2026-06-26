import os
from typing import Optional
from src.api import AllianceProviderBase


class MockAllianceProvider(AllianceProviderBase):
    
    def __init__(self):
        self.enabled = os.getenv("ALLIANCE_API_ENABLED", "false").lower() == "true"
    
    @property
    def provider_name(self) -> str:
        return "MOCK"
    
    @property
    def is_enabled(self) -> bool:
        return True
    
    async def health_check(self) -> dict:
        return {
            "status": "HEALTHY",
            "provider": self.provider_name,
            "enabled": True,
            "message": "Mock provider active for testing"
        }
    
    async def fetch_alliance(self, alliance_tag: str) -> Optional[dict]:
        return {
            "alliance_tag": alliance_tag,
            "alliance_name": f"Mock Alliance {alliance_tag}",
            "external_id": f"mock_{alliance_tag}",
        }
    
    async def fetch_alliance_members(self, alliance_tag: str) -> list[dict]:
        return [
            {
                "player_id": "11111111",
                "rank": "R5",
                "alliance_tag": alliance_tag,
                "alliance_name": f"Mock Alliance {alliance_tag}",
                "last_seen_at": "2026-06-26T12:00:00Z",
            },
            {
                "player_id": "22222222",
                "rank": "R4",
                "alliance_tag": alliance_tag,
                "alliance_name": f"Mock Alliance {alliance_tag}",
                "last_seen_at": "2026-06-26T11:00:00Z",
            },
        ]
    
    async def fetch_player(self, player_id: str) -> Optional[dict]:
        return {
            "player_id": player_id,
            "rank": "R3",
            "alliance_tag": "MOCK",
            "alliance_name": "Mock Alliance",
        }
