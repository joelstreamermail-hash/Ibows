# Commands/admin_commands.py
import discord
import json
from discord import app_commands, Interaction, Embed
from discord.ext import commands

class AdminCommands(app_commands.Group):
    """Spezialisierte Bot-Admin Commands."""
    def __init__(self, bot: commands.Bot):
        super().__init__(name="admin", description="Spezialisierte Bot-Admin Commands")
        self.bot = bot
    
    @app_commands.command(name="show_config_raw", description="Zeigt die aktuelle JSON-Bot-Konfiguration (Nur für Bot-Admins).")
    @app_commands.default_permissions(administrator=True)
    async def show_config_raw(self, interaction: Interaction):
        # Sicherheit: Nur echte Administratoren sollen dies sehen
        if not interaction.user.guild_permissions.administrator:
             return await interaction.response.send_message("❌ Keine Berechtigung.", ephemeral=True)
             
        config_data = self.bot.setup_data.get(str(interaction.guild_id), "Keine Konfiguration gespeichert.")
        
        # Stellt sicher, dass das JSON im Code-Block lesbar ist
        config_str = json.dumps(config_data, indent=2)

        embed = Embed(
            title="⚙️ Aktuelle Bot-Konfiguration (RAW)",
            description=f"```json\n{config_str}\n```",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)