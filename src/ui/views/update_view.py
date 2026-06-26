import discord
from discord import ui

from src.ui.components.embeds import create_section_embed, create_unauthorized_embed


class UpdateView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="🔎 فحص تحديث",
            custom_id="wos:update:check",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="📋 خطة تحديث",
            custom_id="wos:update:plan",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="⬆️ تطبيق تحديث",
            custom_id="wos:update:apply_confirm",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:update:back",
            row=2
        ))


class UpdateConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="✅ تأكيد التحديث",
            custom_id="wos:update:apply_execute",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="❌ إلغاء",
            custom_id="wos:update:apply_cancel",
            row=0
        ))
