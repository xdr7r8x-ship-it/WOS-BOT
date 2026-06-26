from dataclasses import dataclass
from typing import Optional


@dataclass
class ViewState:
    section: str
    view_name: str
    action: str = ""
    guild_id: str = ""
    user_id: str = ""
    page: int = 1
    alliance_id: int = None
    alliance_tag: str = ""
    player_id: str = ""
    timestamp: int = 0

    def to_dict(self) -> dict:
        return {
            "section": self.section,
            "view": self.view_name,
            "action": self.action,
            "guild_id": self.guild_id,
            "user_id": self.user_id,
            "page": self.page,
            "alliance_id": self.alliance_id,
            "alliance_tag": self.alliance_tag,
            "player_id": self.player_id,
            "ts": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Optional["ViewState"]:
        if not data:
            return None
        try:
            return cls(
                section=data.get("section", ""),
                view_name=data.get("view", ""),
                action=data.get("action", ""),
                guild_id=data.get("guild_id", ""),
                user_id=data.get("user_id", ""),
                page=data.get("page", 1),
                alliance_id=data.get("alliance_id"),
                alliance_tag=data.get("alliance_tag", ""),
                player_id=data.get("player_id", ""),
                timestamp=data.get("ts", 0),
            )
        except Exception:
            return None


def get_default_state(user_id: str, guild_id: str) -> ViewState:
    return ViewState(
        section="main",
        view_name="MainView",
        user_id=user_id,
        guild_id=guild_id,
    )
