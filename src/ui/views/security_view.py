import discord
from discord import ui

from src.ui.components.embeds import create_section_embed, create_field_embed, create_success_embed, create_unauthorized_embed
from src.ui.components.guards import check_admin_permission, log_panel_action


class SecurityView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="🔍 فحص الحماية",
            custom_id="wos:security:scan",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="📜 Audit Logs",
            custom_id="wos:security:audit",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🚫 المحظورين",
            custom_id="wos:security:blocked",
            row=2
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="⚠️ الحوادث الأمنية",
            custom_id="wos:security:incidents",
            row=2
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:security:back",
            row=3
        ))
