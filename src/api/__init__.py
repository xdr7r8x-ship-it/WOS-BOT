from abc import ABC, abstractmethod
from typing import Optional


class AllianceProviderBase(ABC):
    
    @abstractmethod
    async def health_check(self) -> dict:
        pass

    @abstractmethod
    async def fetch_alliance(self, alliance_tag: str) -> Optional[dict]:
        pass

    @abstractmethod
    async def fetch_alliance_members(self, alliance_tag: str) -> list[dict]:
        pass

    @abstractmethod
    async def fetch_player(self, player_id: str) -> Optional[dict]:
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def is_enabled(self) -> bool:
        pass