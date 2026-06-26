import discord
from discord import ui

from src.ui.components.embeds import create_section_embed, create_unauthorized_embed


class MaintenanceView(ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.add_buttons()

    def add_buttons(self):
        self.add_item(ui.Button(
            style=discord.ButtonStyle.success,
            label="🧹 Cleanup",
            custom_id="wos:maintenance:cleanup",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.success,
            label="🔁 Retry Jobs",
            custom_id="wos:maintenance:retry",
            row=0
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.secondary,
            label="📄 Logs Status",
            custom_id="wos:maintenance:logs",
            row=1
        ))
        self.add_item(ui.Button(
            style=discord.ButtonStyle.gray,
            label="⬅️ رجوع",
            custom_id="wos:maintenance:back",
            row=2
        ))
