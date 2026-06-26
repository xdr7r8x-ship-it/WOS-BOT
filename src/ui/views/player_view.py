import discord
from discord import ui

from src.ui.components.embeds import create_section_embed, create_unauthorized_embed
from src.ui.components.guards import check_admin_permission, log_panel_action


class PlayerView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary,
            label="📋 قائمة اللاعبين",
            custom_id="wos:players:list",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="➖ تعطيل لاعب",
            custom_id="wos:players:remove",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="📊 عدد اللاعبين",
            custom_id="wos:players:count",
            row=2
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:players:back",
            row=3
        ))


class PlayerRemoveModal(ui.Modal, title="تعطيل لاعب"):
    player_id = ui.TextInput(
        label="Player ID",
        placeholder="أدخل Player ID",
        required=True,
        max_length=20
    )

    async def on_submit(self, interaction: discord.Interaction):
        from src.ui.components.embeds import create_success_embed, create_error_embed
        from src.utils.validators import validate_player_id
        from database import disable_player, get_player

        guild_id = str(interaction.guild_id) if interaction.guild else "0"
        user_id = str(interaction.user.id) if interaction.user else "0"

        allowed, reason = await check_admin_permission(interaction, "player_remove")
        if not allowed:
            await interaction.response.send_message(
                embed=create_unauthorized_embed(),
                ephemeral=True
            )
            return

        player_id_input = self.player_id.value.strip()

        if not validate_player_id(player_id_input):
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", "Player ID غير صالح"),
                ephemeral=True
            )
            return

        player = get_player(guild_id, player_id_input)
        if not player:
            await interaction.response.send_message(
                embed=create_error_embed("⚠️", "اللاعب غير موجود"),
                ephemeral=True
            )
            return

        if disable_player(guild_id, player_id_input):
            log_panel_action(guild_id, user_id, "PLAYER_DISABLED", f"player:{player_id_input}", "SUCCESS", "MEDIUM")
            await interaction.response.send_message(
                embed=create_success_embed("✅ تم", f"تم تعطيل اللاعب {player_id_input}"),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", "فشل في تعطيل اللاعب"),
                ephemeral=True
            )
