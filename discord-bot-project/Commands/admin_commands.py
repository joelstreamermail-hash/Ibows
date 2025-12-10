# Commands/admin_commands.py
import discord
from discord import app_commands, Interaction, Embed
from discord.ext import commands

class AdminCommands(app_commands.Group):
    """
    Spezialisierte Bot-Admin Commands.
    Diese Commands sind typischerweise nur für die Bot-Entwickler oder höchste Server-Admins gedacht.
    """
    def __init__(self, bot: commands.Bot):
        super().__init__(name="admin", description="Spezialisierte Bot-Admin Commands")
        self.bot = bot
    
    # ----------------------------------------------------
    # Beispiel Command: Zeigt den aktuellen Setup-Status im Detail
    # ----------------------------------------------------
    @app_commands.command(name="show_config_raw", description="Zeigt die aktuelle JSON-Bot-Konfiguration (Nur für Bot-Admins).")
    @app_commands.default_permissions(administrator=True) # Nur Admins können diesen Befehl sehen
    async def show_config_raw(self, interaction: Interaction):
        # Prüfung, ob der User wirklich Administrator ist (oder eine spezifische Bot-Rolle hat)
        if not interaction.user.guild_permissions.administrator:
             return await interaction.response.send_message("❌ Nur für Server-Administratoren.", ephemeral=True)
             
        # Bereinigt und formatiert die gespeicherte JSON-Konfiguration
        config_data = self.bot.setup_data.get(str(interaction.guild_id), "Keine Konfiguration gespeichert.")
        
        # Stellt sicher, dass das JSON im Code-Block lesbar ist
        import json
        config_str = json.dumps(config_data, indent=2)

        embed = Embed(
            title="⚙️ Aktuelle Bot-Konfiguration (RAW)",
            description=f"```json\n{config_str}\n```",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)