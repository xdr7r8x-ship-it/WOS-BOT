import discord
from discord import ui

from src.i18n import t
from src.services.player_id_service import register_player_id, update_player_id, delete_player_id, get_player_id


class RegisterPlayerIDModal(ui.Modal, title=""):
    def __init__(self, user_id: str, guild_id: str, lang: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        
        self.player_id = ui.TextInput(
            label=t("player_id.enter_id", lang),
            placeholder=t("player_id.placeholder", lang),
            max_length=15,
            min_length=6,
            required=True
        )
        self.add_item(self.player_id)

    async def callback(self, interaction: discord.Interaction):
        from src.services.player_id_service import register_player_id
        
        player_id_value = self.player_id.value.strip()
        
        success, message = register_player_id(
            guild_id=self.guild_id,
            discord_user_id=self.user_id,
            player_id=player_id_value
        )
        
        if success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.success", self.lang),
                    description=t("player_id.registered", self.lang),
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=message,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )


class UpdatePlayerIDModal(ui.Modal, title=""):
    def __init__(self, user_id: str, guild_id: str, lang: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        
        self.player_id = ui.TextInput(
            label=t("player_id.enter_new_id", lang),
            placeholder=t("player_id.placeholder", lang),
            max_length=15,
            min_length=6,
            required=True
        )
        self.add_item(self.player_id)

    async def callback(self, interaction: discord.Interaction):
        from src.services.player_id_service import update_player_id
        
        player_id_value = self.player_id.value.strip()
        
        success, message = update_player_id(
            guild_id=self.guild_id,
            discord_user_id=self.user_id,
            new_player_id=player_id_value
        )
        
        if success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.success", self.lang),
                    description=t("player_id.updated", self.lang),
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=message,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )


class DeletePlayerIDModal(ui.Modal, title=""):
    def __init__(self, user_id: str, guild_id: str, lang: str):
        super().__init__(timeout=300)
        self.user_id = user_id
        self.guild_id = guild_id
        self.lang = lang
        
        self.confirm = ui.TextInput(
            label=t("player_id.confirm_delete", lang),
            placeholder=t("player_id.confirm_placeholder", lang),
            max_length=10,
            required=True
        )
        self.add_item(self.confirm)

    async def callback(self, interaction: discord.Interaction):
        from src.services.player_id_service import delete_player_id
        
        if self.confirm.value.strip().lower() != "delete":
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=t("player_id.delete_cancelled", self.lang),
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
        
        success, message = delete_player_id(
            guild_id=self.guild_id,
            discord_user_id=self.user_id
        )
        
        if success:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.success", self.lang),
                    description=t("player_id.deleted", self.lang),
                    color=discord.Color.green()
                ),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=t("common.error", self.lang),
                    description=message,
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
