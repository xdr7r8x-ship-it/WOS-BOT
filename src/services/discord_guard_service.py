import re
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import discord


MENTION_PATTERNS = [
    "@everyone",
    "@here",
    r"<@!?\d+>",
]


class DiscordGuardService:
    def __init__(self):
        self.max_message_length = 2000
        self._allowed_mentions = None
        
    def get_allowed_mentions(self):
        if self._allowed_mentions is None:
            import discord
            self._allowed_mentions = discord.AllowedMentions.none()
        return self._allowed_mentions
    
    def clean_content(self, content: str) -> str:
        if not content:
            return content
        
        for pattern in MENTION_PATTERNS:
            content = re.sub(pattern, "", content, flags=re.IGNORECASE)
        
        return content.strip()
    
    def sanitize_for_embed(self, text: str) -> str:
        if not text:
            return text
        
        text = text.replace("@everyone", "@\u200Beveryone")
        text = text.replace("@here", "@\u200Bhere")
        text = re.sub(r"<@!?(\d+)>", "@user", text)
        
        text = text.replace("{", "\u200B{")
        text = text.replace("}", "\u200B}")
        
        return text[:1024]
    
    def is_safe_message(self, message) -> tuple[bool, str]:
        if hasattr(message, 'author') and getattr(message.author, 'bot', False):
            return False, "Bot user"
        
        if hasattr(message, 'guild') and message.guild is None:
            return True, "DM"
        
        content = getattr(message, 'content', '') or ''
        if len(content) > 10000:
            return False, "Message too long"
        
        if content.count("@") > 50:
            return False, "Mass mention suspected"
        
        return True, "Safe"
    
    def check_webhook(self, message) -> bool:
        if hasattr(message, 'webhook_id') and message.webhook_id:
            return True
        return False
    
    def extract_safe_content(self, content: str) -> str:
        if not content:
            return ""
        
        content = re.sub(r"<@!?\d+>", "", content)
        content = re.sub(r"@everyone", "", content, flags=re.IGNORECASE)
        content = re.sub(r"@here", "", content, flags=re.IGNORECASE)
        
        return content.strip()[:2000]
    
    def format_safe_response(self, content: str) -> dict:
        return {
            "content": self.extract_safe_content(content),
            "allowed_mentions": self.get_allowed_mentions()
        }


discord_guard_service = DiscordGuardService()
