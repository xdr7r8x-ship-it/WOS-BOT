import discord
from discord import ui

from src.i18n import t
from src.services.content_service import get_text, set_text
from src.services.content_registry_service import get_block_max_length
from src.services.content_audit_service import save_content_audit
from src.utils.content_sanitizer import sanitize_content


class EditContentModal(ui.Modal, title=""):
    def __init__(self, user_id: str, guild_id: str, page_key: str, block_key: str, lang: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.page_key = page_key
        self.block_key = block_key
        self.lang = lang
        
        max_length = get_block_max_length(page_key, block_key, lang)
        current_text = get_text(guild_id, page_key, block_key, lang)
        
        self.new_text_input = ui.TextInput(
            label=t("content.current_text", lang),
            style=discord.TextStyle.long,
            placeholder=current_text[:100] if len(current_text) > 100 else current_text,
            default_value=current_text[:400] if len(current_text) > 400 else current_text,
            max_length=max_length,
            required=True
        )
        self.add_item(self.new_text_input)

    async def callback(self, interaction: discord.Interaction):
        new_text = self.new_text_input.value.strip()
        
        sanitized = sanitize_content(new_text, get_block_max_length(self.page_key, self.block_key, self.lang))
        
        if not sanitized.is_valid:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=sanitized.error,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            save_content_audit(
                self.guild_id, self.user_id, "CONTENT_SECURITY_REJECTED",
                self.page_key, self.block_key, self.lang,
                "REJECTED", "MEDIUM",
                f'{{"reason": "Security: {sanitized.error}"}}'
            )
            return
        
        success, message = set_text(
            self.guild_id, self.page_key, self.block_key, self.lang,
            sanitized.sanitized_text, self.user_id
        )
        
        if success:
            save_content_audit(
                self.guild_id, self.user_id, "PAGE_CONTENT_UPDATED",
                self.page_key, self.block_key, self.lang,
                "SUCCESS", "LOW",
                f'{{"length": {len(sanitized.sanitized_text)}}}'
            )
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.success", self.lang),
                    description=t("content.updated_message", self.lang),
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        else:
            save_content_audit(
                self.guild_id, self.user_id, "PAGE_CONTENT_UPDATE_FAILED",
                self.page_key, self.block_key, self.lang,
                "FAILED", "MEDIUM",
                f'{{"error": "Database error"}}'
            )
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=t("errors.generic", self.lang),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
