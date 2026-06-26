import discord
from discord import ui

from src.ui.components.embeds import create_section_embed, create_success_embed, create_error_embed, create_timeout_embed


class RedeemView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.primary,
            label="➕ استرداد كود",
            custom_id="wos:redeem:add",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🔎 حالة كود",
            custom_id="wos:redeem:status",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="📋 حالة Queue",
            custom_id="wos:redeem:queue",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:redeem:back",
            row=2
        ))


class RedeemCodeModal(ui.Modal, title="استرداد كود"):
    code = ui.TextInput(
        label="Gift Code",
        placeholder="أدخل الكود هنا",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        from src.ui.components.guards import log_panel_action
        from src.ui.components.embeds import create_success_embed, create_error_embed
        from src.utils.validators import normalize_gift_code, validate_gift_code
        from database import (
            generate_code_hash, code_exists_in_gift_codes, 
            code_exists_in_processed, add_gift_code, 
            update_code_status, get_active_players
        )
        from src.services.queue_service import queue_service

        guild_id = str(interaction.guild_id) if interaction.guild else "0"
        user_id = str(interaction.user.id) if interaction.user else "0"
        
        code_input = self.code.value.strip().upper()
        code_input = normalize_gift_code(code_input)

        if not validate_gift_code(code_input):
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", "كود غير صالح"),
                ephemeral=True
            )
            return

        code_hash = generate_code_hash(guild_id, code_input)

        if code_exists_in_gift_codes(guild_id, code_hash) or code_exists_in_processed(guild_id, code_hash):
            await interaction.response.send_message(
                embed=create_error_embed("⚠️ تنبيه", "الكود تمت معالجته مسبقًا"),
                ephemeral=True
            )
            return

        players = get_active_players(guild_id)
        success, _ = add_gift_code(guild_id, code_input, code_hash)

        if success:
            update_code_status(guild_id, code_hash, "QUEUED")
            queue_service.enqueue(guild_id, code_hash)
            log_panel_action(guild_id, user_id, "REDEEM_CODE_QUEUED", code_input, "SUCCESS", "MEDIUM")
            await interaction.response.send_message(
                embed=create_success_embed("✅ تم", f"تم إرسال الكود إلى قائمة المعالجة ({len(players)} لاعب)"),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                embed=create_error_embed("❌ خطأ", "فشل في إضافة الكود"),
                ephemeral=True
            )


class StatusCodeModal(ui.Modal, title="حالة الكود"):
    code = ui.TextInput(
        label="Gift Code",
        placeholder="أدخل الكود هنا",
        required=True,
        max_length=50
    )

    async def on_submit(self, interaction: discord.Interaction):
        from src.ui.components.guards import log_panel_action
        from src.ui.components.embeds import create_field_embed
        from src.utils.validators import normalize_gift_code
        from database import generate_code_hash, get_code_by_hash, get_processed_code

        guild_id = str(interaction.guild_id) if interaction.guild else "0"
        user_id = str(interaction.user.id) if interaction.user else "0"

        code_input = self.code.value.strip().upper()
        code_input = normalize_gift_code(code_input)
        code_hash = generate_code_hash(guild_id, code_input)

        code_info = get_code_by_hash(guild_id, code_hash)
        if not code_info:
            code_info = get_processed_code(guild_id, code_hash)

        log_panel_action(guild_id, user_id, "CODE_STATUS_VIEWED", "code_lookup", "SUCCESS", "LOW")

        if code_info:
            status = code_info.get("status", "UNKNOWN")
            status_emoji = "🔵" if status == "QUEUED" else "🟡" if status == "PROCESSING" else "✅" if status == "COMPLETED" else "🔴"
            embed = create_field_embed(
                "🔎 حالة الكود",
                [
                    ("الحالة", f"{status_emoji} {status}", True),
                    ("تاريخ الإضافة", code_info.get("created_at", "N/A")[:10], True),
                ]
            )
        else:
            embed = create_field_embed(
                "🔎 حالة الكود",
                [("النتيجة", "الكود غير موجود", True)]
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)
