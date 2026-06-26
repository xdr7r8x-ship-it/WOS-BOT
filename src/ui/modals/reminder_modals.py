import discord
from discord import ui

from src.i18n import t
from src.services.reminder_service import create_reminder, REMINDER_TIME_MODES, REMINDER_RECURRENCES, DEFAULT_OFFSETS


class CreateReminderModal(ui.Modal, title=""):
    def __init__(self, user_id: str, guild_id: str, lang: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        
        self.event_name = ui.TextInput(
            label=t("reminder.event_name", lang),
            placeholder=t("reminder.event_placeholder", lang),
            max_length=100,
            required=True
        )
        self.add_item(self.event_name)
        
        self.event_time = ui.TextInput(
            label=t("reminder.event_time", lang),
            placeholder="21:00",
            max_length=5,
            required=True
        )
        self.add_item(self.event_time)
        
        self.channel_id = ui.TextInput(
            label=t("reminder.channel_id", lang),
            placeholder=t("reminder.channel_placeholder", lang),
            max_length=20,
            required=True
        )
        self.add_item(self.channel_id)

    async def callback(self, interaction: discord.Interaction):
        from src.services.reminder_service import get_time_settings, set_time_settings, save_reminder_audit
        from datetime import datetime
        
        time_settings = get_time_settings(self.guild_id)
        
        event_time_str = self.event_time.value.strip()
        
        try:
            hour, minute = event_time_str.split(":")
            event_time = f"{hour}:{minute}"
        except:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=t("reminder.invalid_time_format", self.lang),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
        
        event_time_utc = f"2026-01-01T{event_time}:00"
        event_time_local = event_time
        
        try:
            success, reminder_id = create_reminder(
                guild_id=self.guild_id,
                channel_id=self.channel_id.value.strip(),
                event_name=self.event_name.value.strip(),
                event_time_local=event_time_local,
                event_time_utc=event_time_utc,
                source_timezone=time_settings["real_timezone"],
                time_mode="REAL_TIME",
                recurrence="NONE",
                role_id=None,
                created_by=self.user_id,
                offsets=DEFAULT_OFFSETS
            )
            
            if success:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=t("common.success", self.lang),
                        description=t("reminder.created", self.lang),
                        color=discord.Color.green()
                    ),
                    ephemeral=True
                )
            else:
                await interaction.response.send_message(
                    embed=discord.Embed(
                        title=t("common.error", self.lang),
                        description=t("errors.generic", self.lang),
                        color=discord.Color.red()
                    ),
                    ephemeral=True
                )
        except Exception as e:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=str(e)[:200],
                    color=discord.Color.red()
                ),
                ephemeral=True
            )


class TimeSettingsModal(ui.Modal, title=""):
    def __init__(self, user_id: str, guild_id: str, lang: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        
        from src.services.reminder_service import get_time_settings
        settings = get_time_settings(guild_id)
        
        self.game_timezone = ui.TextInput(
            label=t("reminder.game_timezone", lang),
            default_value=settings["game_timezone"],
            placeholder="UTC",
            max_length=50,
            required=True
        )
        self.add_item(self.game_timezone)
        
        self.real_timezone = ui.TextInput(
            label=t("reminder.real_timezone", lang),
            default_value=settings["real_timezone"],
            placeholder="Asia/Riyadh",
            max_length=50,
            required=True
        )
        self.add_item(self.real_timezone)

    async def callback(self, interaction: discord.Interaction):
        from src.services.reminder_service import set_time_settings
        
        success = set_time_settings(
            guild_id=self.guild_id,
            game_timezone=self.game_timezone.value.strip(),
            real_timezone=self.real_timezone.value.strip()
        )
        
        if success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.success", self.lang),
                    description=t("reminder.settings_saved", self.lang),
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=t("errors.generic", self.lang),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
