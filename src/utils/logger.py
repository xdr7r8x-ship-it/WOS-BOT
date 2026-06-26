import logging
import sys
from datetime import datetime


class BotLogger:
    def __init__(self, name: str = "wos-bot"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def info(self, message: str, **kwargs):
        self.logger.info(message)
        guild_id = kwargs.get("guild_id")
        if guild_id:
            from database import log_system
            log_system(str(guild_id), "INFO", "INFO", message)
    
    def warning(self, message: str, **kwargs):
        self.logger.warning(message)
        guild_id = kwargs.get("guild_id")
        if guild_id:
            from database import log_system
            log_system(str(guild_id), "WARNING", "WARNING", message)
    
    def error(self, message: str, **kwargs):
        self.logger.error(message)
        guild_id = kwargs.get("guild_id")
        if guild_id:
            from database import log_system
            log_system(str(guild_id), "ERROR", "ERROR", message)
    
    def critical(self, message: str, **kwargs):
        self.logger.critical(message)
        guild_id = kwargs.get("guild_id")
        if guild_id:
            from database import log_system
            log_system(str(guild_id), "CRITICAL", "CRITICAL", message)
    
    def debug(self, message: str, **kwargs):
        self.logger.debug(message)


bot_logger = BotLogger()
