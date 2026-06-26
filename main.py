import asyncio
import logging
import os
import re
import sys
from datetime import datetime

import discord
from discord import app_commands
from discord.ext import commands

from database import (
    init_database,
    get_guild_settings,
    save_guild_settings,
    register_player,
    get_active_players,
    get_player_count,
    disable_player,
    add_gift_code,
    update_code_status,
    generate_code_hash,
    code_exists_in_gift_codes,
    code_exists_in_processed,
    get_code_by_hash,
    get_processed_code,
    log_system,
    save_system_state,
    get_backups,
    get_health_events,
    get_security_events,
    get_prediction_events,
    save_audit_log,
)
from src.utils.validators import validate_player_id, validate_gift_code, normalize_gift_code, extract_codes_from_text
from src.utils.config import load_config
from src.utils.time import format_uptime
from src.utils.system import get_memory_info, get_disk_info, get_uptime
from src.services.queue_service import queue_service
from src.services.redeem_service import redeem_service
from src.services.retry_service import retry_service
from src.services.recovery_service import recovery_service
from src.services.cleanup_service import cleanup_service
from src.services.health_service import health_service
from src.services.autopilot_service import autopilot_service
from src.services.version_service import read_version
from src.services.backup_service import backup_service
from src.services.rollback_service import rollback_service
from src.services.update_service import update_service
from src.services.diagnostics_service import diagnostics_service
from src.services.security_service import security_service
from src.services.integrity_service import integrity_service
from src.services.alert_service import alert_service
from src.utils.logger import bot_logger
from src.services.security_hardening_service import security_hardening_service
from src.services.abuse_guard_service import abuse_guard_service
from src.ui.wos_panel import handle_wos_command, handle_button

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

SAFE_ALLOWED_MENTIONS = discord.AllowedMentions.none()


class SetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.register_channel = None
        self.codes_channel = None
        self.log_channel = None
        self.admin_role = None

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="Register Channel",
        row=0,
    )
    async def register_channel_select(self, interaction, select):
        self.register_channel = select.values[0]
        await interaction.response.send_message(f"Register: {self.register_channel.mention}", ephemeral=True)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="Codes Channel",
        row=1,
    )
    async def codes_channel_select(self, interaction, select):
        self.codes_channel = select.values[0]
        await interaction.response.send_message(f"Codes: {self.codes_channel.mention}", ephemeral=True)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        channel_types=[discord.ChannelType.text],
        placeholder="Log Channel (optional)",
        row=2,
    )
    async def log_channel_select(self, interaction, select):
        self.log_channel = select.values[0]
        await interaction.response.send_message(f"Log: {self.log_channel.mention}", ephemeral=True)

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Admin Role (optional)",
        row=3,
    )
    async def admin_role_select(self, interaction, select):
        self.admin_role = select.values[0]
        await interaction.response.send_message(f"Admin: {self.admin_role.mention}", ephemeral=True)

    @discord.ui.button(label="Save", style=discord.ButtonStyle.green, row=4)
    async def save_button(self, interaction, button):
        save_guild_settings(
            str(interaction.guild_id),
            register_channel_id=str(self.register_channel.id) if self.register_channel else None,
            codes_channel_id=str(self.codes_channel.id) if self.codes_channel else None,
            log_channel_id=str(self.log_channel.id) if self.log_channel else None,
            admin_role_id=str(self.admin_role.id) if self.admin_role else None,
        )
        embed = discord.Embed(title="✅ Setup Complete", color=0x00FF00)
        embed.add_field(name="Register Channel", value=self.register_channel.mention if self.register_channel else "Not set")
        embed.add_field(name="Codes Channel", value=self.codes_channel.mention if self.codes_channel else "Not set")
        embed.add_field(name="Log Channel", value=self.log_channel.mention if self.log_channel else "Not set")
        embed.add_field(name="Admin Role", value=self.admin_role.mention if self.admin_role else "Not set")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()


@tree.command(name="wos", description="Open WOS-BOT control panel")
async def wos_command(interaction):
    await handle_wos_command(interaction)


# All other slash commands have been removed
# All functionality is now accessible via /wos panel
# To clear old commands from Discord, run: CONFIRM_CLEAR_COMMANDS=true python scripts/clear_old_commands.py


async def process_registration(message: discord.Message):
    guild_id = str(message.guild.id)
    user_id = str(message.author.id)
    settings = get_guild_settings(guild_id)
    
    if not settings or not settings.get("register_channel_id"):
        return
    
    if message.channel.id != int(settings["register_channel_id"]):
        return
    
    if security_hardening_service.is_user_blocked(guild_id, user_id):
        await message.reply("⏳ أنت محظور مؤقتًا. حاول لاحقًا.")
        return
    
    content = message.content.strip()
    
    valid, reason = security_hardening_service.validate_player_id(content)
    if not valid:
        await security_hardening_service.record_invalid_input(guild_id, user_id, "register", content)
        await message.reply("❌")
        return
    
    success, status = register_player(guild_id, content)
    
    if success:
        save_audit_log(guild_id, user_id, "PLAYER_REGISTERED", f"player:{content}", "SUCCESS", "LOW", f"Player {content} registered")
        await message.reply("✅ تم تسجيل اللاعب بنجاح")
    elif status == "EXISTS":
        await message.reply("مسجل مسبقًا")
    else:
        await message.reply("❌")


async def process_codes(message: discord.Message):
    guild_id = str(message.guild.id)
    user_id = str(message.author.id)
    settings = get_guild_settings(guild_id)
    
    if not settings or not settings.get("codes_channel_id"):
        return
    
    if message.channel.id != int(settings["codes_channel_id"]):
        return
    
    allowed, reason = security_hardening_service.check_abuse(guild_id, user_id, "redeem")
    if not allowed:
        return
    
    codes = extract_codes_from_text(message.content)
    
    for code in codes:
        code_hash = generate_code_hash(guild_id, code)
        
        if code_exists_in_gift_codes(guild_id, code_hash) or code_exists_in_processed(guild_id, code_hash):
            continue
        
        players = get_active_players(guild_id)
        
        success, _ = add_gift_code(guild_id, code, code_hash, str(message.id))
        
        if success:
            update_code_status(guild_id, code_hash, "QUEUED")
            queue_service.enqueue(guild_id, code_hash)
            
            embed = discord.Embed(title="🔵 تم اكتشاف كود جديد", color=0x3498DB)
            embed.add_field(name="Status", value="Queued")
            embed.add_field(name="Players", value=str(len(players)))
            await message.reply(embed=embed)


async def process_queue():
    while True:
        try:
            for guild_id in list(queue_service._queues.keys()):
                code_hash = await queue_service.dequeue(guild_id)
                
                if code_hash:
                    code_info = get_code_by_hash(guild_id, code_hash)
                    
                    if code_info:
                        await redeem_service.process_code(guild_id, code_info["code"], code_info.get("source_message_id"))
                    
                    await queue_service.mark_complete(guild_id, code_hash)
        except Exception as e:
            bot_logger.error(f"Queue processing error: {e}")
        
        await asyncio.sleep(1)


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    
    if not message.guild:
        return
    
    safe, reason = security_hardening_service.check_message_safety(message)
    if not safe:
        return
    
    try:
        await process_registration(message)
    except Exception as e:
        bot_logger.error(f"Registration error: {e}")
    
    try:
        await process_codes(message)
    except Exception as e:
        bot_logger.error(f"Code processing error: {e}")
    
    await bot.process_commands(message)


@bot.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.type == discord.InteractionType.component:
        custom_id = interaction.data.get("custom_id", "")
        if custom_id.startswith("wos:"):
            await handle_button(interaction)


@bot.event
async def on_ready():
    await tree.sync()
    logger.info(f"Bot ready as {bot.user}")
    
    init_database()
    
    from database import init_autopilot_tables
    init_autopilot_tables()
    
    from src.services.version_service import read_version
    from database import save_system_state
    version = read_version()
    if version:
        save_system_state("version", version)
    
    if security_hardening_service.config.get('SECURITY_SCAN_ON_STARTUP', True):
        try:
            results = security_service.run_security_scan()
            if results["overall_status"] == "FAIL":
                bot_logger.warning("Startup security scan failed")
        except Exception as e:
            bot_logger.error(f"Startup security scan error: {e}")
    
    await recovery_service.recover_all()
    
    bot.loop.create_task(process_queue())
    bot.loop.create_task(retry_service.start())
    bot.loop.create_task(cleanup_service.start())
    
    try:
        await autopilot_service.start()
        logger.info("Autopilot services started")
    except Exception as e:
        logger.error(f"Failed to start autopilot: {e}")
    
    try:
        await alert_service.send_startup_alert()
    except Exception:
        pass
    
    logger.info("All services started")


async def safe_shutdown():
    logger.info("Initiating safe shutdown...")
    
    try:
        await autopilot_service.stop()
    except Exception:
        pass
    
    try:
        from database import save_system_state
        save_system_state("shutdown_at", str(datetime.utcnow()))
    except Exception:
        pass
    
    logger.info("Safe shutdown complete")


def main():
    load_config()
    init_database()
    
    try:
        bot.run(TOKEN)
    finally:
        bot.loop.run_until_complete(safe_shutdown())


if __name__ == "__main__":
    main()
