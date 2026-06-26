import discord
from discord import ui

from src.ui.components.embeds import create_main_embed
from src.i18n import t
from src.services.admin_access_service import check_permission


class MainView(ui.View):
    def __init__(self, user_id: str = None, guild_id: str = None, lang: str = "ar"):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary,
            label="🎁 " + t("panel.codes", self.lang),
            custom_id="wos:main:redeem",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary,
            label="👥 " + t("panel.players", self.lang),
            custom_id="wos:main:players",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.success,
            label="🏰 " + t("panel.alliances", self.lang),
            custom_id="wos:main:alliance",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="🛡️ " + t("panel.security", self.lang),
            custom_id="wos:main:security",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="⚙️ " + t("panel.system", self.lang),
            custom_id="wos:main:system",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="💾 " + t("panel.backup", self.lang),
            custom_id="wos:main:backup",
            row=2
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🔄 " + t("panel.updates", self.lang),
            custom_id="wos:main:update",
            row=2
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.success,
            label="🧹 " + t("panel.maintenance", self.lang),
            custom_id="wos:main:maintenance",
            row=3
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.success,
            label="📊 " + t("panel.health", self.lang),
            custom_id="wos:main:health",
            row=3
        ))
        
        if check_permission(self.guild_id, self.user_id, "CONTENT_EDIT"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label=f"📝 {t('content.edit_button', self.lang)}",
                custom_id="wos:content:open:main_panel",
                row=4
            ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label=t("language.button", self.lang),
            custom_id="wos:language:open",
            row=5
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="⏰ " + t("reminder.title", self.lang),
            custom_id="wos:reminder:open",
            row=6
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🔑 " + t("player_id.title", self.lang),
            custom_id="wos:player_id:open",
            row=6
        ))
