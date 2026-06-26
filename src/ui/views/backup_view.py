import discord
from discord import ui

from src.ui.components.embeds import create_section_embed, create_unauthorized_embed


class BackupView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="💾 إنشاء Backup",
            custom_id="wos:backup:create",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="📋 قائمة Backups",
            custom_id="wos:backup:list",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="↩️ Rollback",
            custom_id="wos:backup:rollback_confirm",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:backup:back",
            row=2
        ))


class RollbackConfirmView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.danger,
            label="✅ تأكيد Rollback",
            custom_id="wos:backup:rollback_execute",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="❌ إلغاء",
            custom_id="wos:backup:rollback_cancel",
            row=0
        ))
