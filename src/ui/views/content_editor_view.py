import discord
from discord import ui

from src.i18n import t
from src.services.admin_access_service import check_permission


class ContentEditorButton(ui.View):
    def __init__(self, user_id: str, guild_id: str, page_key: str, lang: str):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.guild_id = guild_id
        self.page_key = page_key
        self.lang = lang
        self.add_buttons()

    def add_buttons(self):
        if check_permission(self.guild_id, self.user_id, "CONTENT_EDIT"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label=f"📝 {t('content.edit_button', self.lang)}",
                custom_id=f"wos:content:open:{self.page_key}",
                row=99
            ))


class ContentEditorMainView(ui.View):
    def __init__(self, user_id: str, guild_id: str, page_key: str, lang: str):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.guild_id = guild_id
        self.page_key = page_key
        self.lang = lang
        self.add_edit_button()
        self.add_cancel_button()

    def add_edit_button(self):
        if check_permission(self.guild_id, self.user_id, "CONTENT_EDIT"):
            self.add_item(ui.Button(
                style=discord.ButtonStyle.primary,
                label=f"📝 {t('content.edit_button', self.lang)}",
                custom_id=f"wos:content:open:{self.page_key}",
                row=0
            ))
            
            self.add_item(ui.Button(
                style=discord.ButtonStyle.secondary,
                label=f"📜 {t('content.history_button', self.lang)}",
                custom_id=f"wos:content:history:{self.page_key}",
                row=0
            ))

    def add_cancel_button(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label=t("common.close", self.lang),
            custom_id="wos:content:cancel",
            row=99
        ))
