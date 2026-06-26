import discord
from discord import ui

from src.i18n import t
from src.services.language_service import set_user_language
from src.ui.components.embeds import create_section_embed, create_success_embed


class LanguageView(ui.View):
    def __init__(self, user_id: str, guild_id: str, current_lang: str):
        super().__init__(timeout=60)
        self.user_id = user_id
        self.guild_id = guild_id
        self.current_lang = current_lang
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary if current_lang != "ar" else discord.ButtonStyle.success,
            label=f"{'✅ ' if current_lang == 'ar' else ''}العربية",
            custom_id="wos:language:set:ar",
            row=0
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary if current_lang != "en" else discord.ButtonStyle.success,
            label=f"{'✅ ' if current_lang == 'en' else ''}English",
            custom_id="wos:language:set:en",
            row=0
        ))
        
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label=t("common.cancel", current_lang),
            custom_id="wos:language:cancel",
            row=1
        ))
