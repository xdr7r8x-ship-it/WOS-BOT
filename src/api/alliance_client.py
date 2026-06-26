import os
from typing import Optional
from src.api import AllianceProviderBase
from src.api.providers import get_provider


class AllianceClient:
    _instance = None
    _provider = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._provider is None:
            self._initialize_provider()
    
    def _initialize_provider(self):
        provider_type = os.getenv("ALLIANCE_API_PROVIDER", "manual").lower()
        enabled = os.getenv("ALLIANCE_API_ENABLED", "false").lower() == "true"
        
        if not enabled:
            provider_type = "manual"
        
        provider_class = get_provider(provider_type)
        self._provider = provider_class()
    
    @property
    def provider(self) -> AllianceProviderBase:
        return self._provider
    
    @property
    def is_api_enabled(self) -> bool:
        return os.getenv("ALLIANCE_API_ENABLED", "false").lower() == "true"
    
    @property
    def is_auto_sync_enabled(self) -> bool:
        return os.getenv("ALLIANCE_API_AUTO_SYNC", "false").lower() == "true"
    
    @property
    def sync_interval_minutes(self) -> int:
        return int(os.getenv("ALLIANCE_API_SYNC_INTERVAL_MINUTES", "60"))
    
    async def health_check(self) -> dict:
        return await self._provider.health_check()
    
    async def fetch_alliance(self, alliance_tag: str) -> Optional[dict]:
        return await self._provider.fetch_alliance(alliance_tag)
    
    async def fetch_alliance_members(self, alliance_tag: str) -> list[dict]:
        return await self._provider.fetch_alliance_members(alliance_tag)
    
    async def fetch_player(self, player_id: str) -> Optional[dict]:
        return await self._provider.fetch_player(player_id)
    
    def reset(self):
        self._provider = None
        self._initialize_provider()


alliance_client = AllianceClient()
