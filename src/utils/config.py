import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    DISCORD_BOT_TOKEN: str
    UPDATE_CHANNEL: str = "stable"
    UPDATE_CHECK_URL: str = ""
    AUTO_APPLY_UPDATES: bool = False
    UPDATES_ENABLED: bool = True
    UPDATE_AUTO_PATCH: bool = True
    UPDATE_AUTO_MINOR: bool = False
    UPDATE_AUTO_MAJOR: bool = False
    LOG_LEVEL: str = "INFO"
    BACKUP_DIR: str = "backups"
    LOGS_DIR: str = "logs"
    DB_DIR: str = "db"
    MAX_BACKUPS: int = 10
    MAX_LOG_SIZE_MB: int = 10
    MAX_LOG_FILES: int = 10
    MONITOR_INTERVAL: int = 60
    WATCHDOG_INTERVAL: int = 60
    PREDICTION_INTERVAL: int = 300
    DIAGNOSTICS_INTERVAL: int = 21600
    BACKUP_INTERVAL: int = 86400
    LOG_ROTATION_INTERVAL: int = 1800
    CLEANUP_INTERVAL: int = 21600
    UPDATE_CHECK_INTERVAL: int = 43200
    MEMORY_WARNING_THRESHOLD: int = 80
    DISK_WARNING_THRESHOLD: int = 85
    MAX_RETRIES: int = 3


_config: Optional[Config] = None


def load_config() -> Config:
    global _config
    if _config is not None:
        return _config
    
    _config = Config(
        DISCORD_BOT_TOKEN=os.getenv("DISCORD_BOT_TOKEN", ""),
        UPDATE_CHANNEL=os.getenv("UPDATE_CHANNEL", "stable"),
        UPDATE_CHECK_URL=os.getenv("UPDATE_CHECK_URL", ""),
        AUTO_APPLY_UPDATES=os.getenv("AUTO_APPLY_UPDATES", "false").lower() == "true",
        UPDATES_ENABLED=os.getenv("UPDATES_ENABLED", "true").lower() == "true",
        UPDATE_AUTO_PATCH=os.getenv("UPDATE_AUTO_PATCH", "true").lower() == "true",
        UPDATE_AUTO_MINOR=os.getenv("UPDATE_AUTO_MINOR", "false").lower() == "true",
        UPDATE_AUTO_MAJOR=os.getenv("UPDATE_AUTO_MAJOR", "false").lower() == "true",
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        BACKUP_DIR=os.getenv("BACKUP_DIR", "backups"),
        LOGS_DIR=os.getenv("LOGS_DIR", "logs"),
        DB_DIR=os.getenv("DB_DIR", "db"),
        MAX_BACKUPS=int(os.getenv("MAX_BACKUPS", "10")),
        MAX_LOG_SIZE_MB=int(os.getenv("MAX_LOG_SIZE_MB", "10")),
        MAX_LOG_FILES=int(os.getenv("MAX_LOG_FILES", "10")),
        MONITOR_INTERVAL=int(os.getenv("MONITOR_INTERVAL", "60")),
        WATCHDOG_INTERVAL=int(os.getenv("WATCHDOG_INTERVAL", "60")),
        PREDICTION_INTERVAL=int(os.getenv("PREDICTION_INTERVAL", "300")),
        DIAGNOSTICS_INTERVAL=int(os.getenv("DIAGNOSTICS_INTERVAL", "21600")),
        BACKUP_INTERVAL=int(os.getenv("BACKUP_INTERVAL", "86400")),
        LOG_ROTATION_INTERVAL=int(os.getenv("LOG_ROTATION_INTERVAL", "1800")),
        CLEANUP_INTERVAL=int(os.getenv("CLEANUP_INTERVAL", "21600")),
        UPDATE_CHECK_INTERVAL=int(os.getenv("UPDATE_CHECK_INTERVAL", "43200")),
        MEMORY_WARNING_THRESHOLD=int(os.getenv("MEMORY_WARNING_THRESHOLD", "80")),
        DISK_WARNING_THRESHOLD=int(os.getenv("DISK_WARNING_THRESHOLD", "85")),
        MAX_RETRIES=int(os.getenv("MAX_RETRIES", "3")),
    )
    return _config


def get_config() -> Config:
    return load_config()
