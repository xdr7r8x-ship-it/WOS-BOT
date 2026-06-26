import os
from typing import List


class Config:
    WEB_DASHBOARD_ENABLED = os.getenv("WEB_DASHBOARD_ENABLED", "true").lower() == "true"
    WEB_DASHBOARD_HOST = os.getenv("WEB_DASHBOARD_HOST", "127.0.0.1")
    WEB_DASHBOARD_PORT = int(os.getenv("WEB_DASHBOARD_PORT", "8080"))
    WEB_PUBLIC_URL = os.getenv("WEB_PUBLIC_URL", "")

    DISCORD_OAUTH_CLIENT_ID = os.getenv("DISCORD_OAUTH_CLIENT_ID", "")
    DISCORD_OAUTH_CLIENT_SECRET = os.getenv("DISCORD_OAUTH_CLIENT_SECRET", "")
    DISCORD_OAUTH_REDIRECT_URI = os.getenv("DISCORD_OAUTH_REDIRECT_URI", "")

    WEB_SESSION_SECRET = os.getenv("WEB_SESSION_SECRET", "")
    WEB_COOKIE_SECURE = os.getenv("WEB_COOKIE_SECURE", "true").lower() == "true"
    WEB_COOKIE_NAME = os.getenv("WEB_COOKIE_NAME", "wos_dashboard_session")
    WEB_SESSION_TTL_HOURS = int(os.getenv("WEB_SESSION_TTL_HOURS", "12"))

    WEB_CORS_ORIGINS = os.getenv("WEB_CORS_ORIGINS", "").split(",") if os.getenv("WEB_CORS_ORIGINS") else []
    WEB_RATE_LIMIT_PER_MINUTE = int(os.getenv("WEB_RATE_LIMIT_PER_MINUTE", "120"))
    WEB_AUDIT_ENABLED = os.getenv("WEB_AUDIT_ENABLED", "true").lower() == "true"

    DATABASE_PATH = os.getenv("DATABASE_PATH", "./db/wos_bot.db")

    @classmethod
    def validate(cls) -> List[str]:
        errors = []
        if not cls.WEB_SESSION_SECRET:
            errors.append("WEB_SESSION_SECRET is required")
        if not cls.DISCORD_OAUTH_CLIENT_ID:
            errors.append("DISCORD_OAUTH_CLIENT_ID is required")
        if not cls.DISCORD_OAUTH_CLIENT_SECRET:
            errors.append("DISCORD_OAUTH_CLIENT_SECRET is required")
        if not cls.DISCORD_OAUTH_REDIRECT_URI:
            errors.append("DISCORD_OAUTH_REDIRECT_URI is required")
        return errors


config = Config()
