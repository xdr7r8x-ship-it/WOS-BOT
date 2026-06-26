import discord
from discord import ui

from src.i18n import t
from src.services.content_service import get_effective_page_content
from src.services.content_registry_service import get_block_max_length


class ContentBlockSelectView(ui.View):
    def __init__(self, user_id: str, guild_id: str, page_key: str, lang: str):
        super().__init__(timeout=120)
        self.user_id = user_id
        self.guild_id = guild_id
        self.page_key = page_key
        self.lang = lang
        
        self.build_select_menu()
        self.add_cancel_button()

    def build_select_menu(self):
        content = get_effective_page_content(self.guild_id, self.page_key, self.lang)
        
        options = []
        for block_key, data in content.items():
            is_custom = data.get("is_custom", False)
            status = "Custom" if is_custom else "Default"
            options.append(
                discord.SelectOption(
                    label=f"{block_key} ({status})",
                    value=f"{block_key}|{is_custom}",
                    description=f"Max: {get_block_max_length(self.page_key, block_key, self.lang)} chars"
                )
            )
        
        if options:
            select = ui.Select(
                placeholder=t("content.select_placeholder", self.lang),
                min_values=1,
                max_values=1,
                options=options[:25],
                custom_id=f"wos:content:select:{self.page_key}"
            )
            select.callback = self.on_select
            self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        if interaction.data.get("values"):
            value = interaction.data["values"][0]
            block_key, is_custom = value.split("|")
            
            from src.ui.modals.edit_content_modal import EditContentModal
            modal = EditContentModal(
                user_id=self.user_id,
                guild_id=self.guild_id,
                page_key=self.page_key,
                block_key=block_key,
                lang=self.lang
            )
            await interaction.response.send_modal(modal)

    def add_cancel_button(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label=t("common.cancel", self.lang),
            custom_id="wos:content:cancel",
            row=99
        ))
