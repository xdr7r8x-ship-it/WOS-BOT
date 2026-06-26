import discord
from discord import ui

from src.services.admin_access_service import add_admin, is_owner, check_permission
from src.ui.components.embeds import create_success_embed, create_error_embed


class AddAdminModal(ui.Modal, title="إضافة أدمن"):
    user_id_input = ui.TextInput(
        label="Discord User ID",
        placeholder="أدخل Discord User ID",
        required=True,
        max_length=25
    )

    async def on_submit(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild_id) if interaction.guild else "0"
        actor_id = str(interaction.user.id) if interaction.user else "0"
        target_id = self.user_id_input.value.strip()
        
        if not check_permission(guild_id, actor_id, "ADMINS_CREATE") and not is_owner(actor_id):
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", "لا تملك صلاحية إضافة أدمن"),
                ephemeral=True
            )
            return
        
        if is_owner(target_id):
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", "لا يمكن إضافة المالك كأدمن"),
                ephemeral=True
            )
            return
        
        import re
        if not re.match(r"^\d{15,25}$", target_id):
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", "Discord User ID غير صالح"),
                ephemeral=True
            )
            return
        
        success, msg = add_admin(guild_id, target_id, actor_id)
        
        if success:
            await interaction.response.send_message(
                embed=create_success_embed("✅ تم", f"تم إضافة الأدمن {target_id}"),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", msg),
                ephemeral=True
            )
