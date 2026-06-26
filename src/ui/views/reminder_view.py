import discord
from discord import ui

from src.i18n import t
from src.services.admin_access_service import check_permission
from src.services.reminder_service import get_upcoming_reminders, get_time_settings


class ReminderView(ui.View):
    def __init__(self, user_id: str, guild_id: str, lang: str = "ar"):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary,
            label=f"➕ {t('reminder.create', self.lang)}",
            custom_id="wos:reminder:create",
            row=0
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"📋 {t('reminder.upcoming', self.lang)}",
            custom_id="wos:reminder:upcoming",
            row=0
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"⏰ {t('reminder.time_settings', self.lang)}",
            custom_id="wos:reminder:settings",
            row=1
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label=f"🗑️ {t('reminder.delete', self.lang)}",
            custom_id="wos:reminder:delete",
            row=1
        ))
        
        if check_permission(self.guild_id, self.user_id, "CONTENT_EDIT"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label=f"📝 {t('content.edit_button', self.lang)}",
                custom_id="wos:content:open:reminder_view",
                row=2
            ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label=t("common.back", self.lang),
            custom_id="wos:main:back",
            row=99
        ))


class PlayerIDSelfServiceView(ui.View):
    def __init__(self, user_id: str, guild_id: str, lang: str = "ar"):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.success,
            label=f"➕ {t('player_id.register', self.lang)}",
            custom_id="wos:player_id:register",
            row=0
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary,
            label=f"📝 {t('player_id.update', self.lang)}",
            custom_id="wos:player_id:update",
            row=0
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label=f"🗑️ {t('player_id.delete', self.lang)}",
            custom_id="wos:player_id:delete",
            row=1
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label=f"📋 {t('player_id.my_id', self.lang)}",
            custom_id="wos:player_id:view",
            row=1
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label=t("common.back", self.lang),
            custom_id="wos:main:back",
            row=99
        ))
