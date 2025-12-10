# discord-bot-project/Commands/admin_commands.py

import discord
import json
from discord import app_commands, Interaction, Embed
from discord.ui import View, Select, Modal, TextInput
from discord.ext import commands
from typing import Literal

# --- HILFSFUNKTIONEN (Müssen hier wiederholt werden, da kein utils.py) ---

def get_role_list(guild: discord.Guild, role_ids: list) -> str:
    """Konvertiert eine Liste von Rollen-IDs in lesbare Namen."""
    if not role_ids:
        return "*(Keine Rollen festgelegt)*"
    roles = [guild.get_role(r_id) for r_id in role_ids if guild.get_role(r_id)]
    return "\n".join([r.mention for r in roles])

def get_channel_mention(guild: discord.Guild, channel_id: int) -> str:
    """Konvertiert eine Kanal-ID in eine Erwähnung."""
    channel = guild.get_channel(channel_id)
    return channel.mention if channel else "*(Kanal nicht gefunden)*"

async def create_setup_embed(interaction: Interaction, config: dict) -> Embed:
    """Erstellt den Embed zur Anzeige der Konfiguration."""
    # (Dieser Code ist identisch zur Version in setup_commands.py)
    guild = interaction.guild
    admin_roles = get_role_list(guild, config.get("admin_role_ids", []))
    log_channel_id = config.get("log_channel_id")
    log_channel = get_channel_mention(guild, log_channel_id) if log_channel_id else "*(Nicht festgelegt)*"
    team_panel_roles = config.get("team_panel_roles", [])
    team_panel_channel_id = config.get("team_panel_channel_id")
    team_panel_channel = get_channel_mention(guild, team_panel_channel_id) if team_panel_channel_id else "*(Nicht festgelegt)*"
    
    team_members_str = ""
    for role_id in team_panel_roles:
        role = guild.get_role(role_id)
        if role:
            members_with_role = [m.mention for m in role.members]
            team_members_str += f"\n**{role.name}** ({len(members_with_role)}): "
            team_members_str += ", ".join(members_with_role) if members_with_role else "Keine Mitglieder."
    
    if not team_members_str: team_members_str = "*(Keine Team-Rollen für das Panel festgelegt)*"
         
    setup_embed = Embed(
        title="⚙️ Bot-Konfiguration & Status",
        description=f"Aktueller Setup-Status für **{guild.name}** (Zugriff via Admin-Command)",
        color=discord.Color.dark_red() # Andere Farbe für Admin-Commands
    )
    
    setup_embed.add_field(name="🔒 Admin/Berechtigungs-Einstellungen", value=f"**Rollen mit Admin-Berechtigung:**\n{admin_roles}", inline=False)
    setup_embed.add_field(name="📊 Logging-Einstellungen", value=f"**Log-Channel:** {log_channel}", inline=True)
    setup_embed.add_field(name="👤 Team-Panel-Einstellungen", value=f"**Panel-Kanal:** {team_panel_channel}", inline=True)
    setup_embed.add_field(name="👥 Team-Übersicht (Aktuelle Mitglieder)", value=team_members_str[:1024], inline=False)
    
    return setup_embed

# --- COMMANDS KLASSE ---

class AdminCommands(app_commands.Group):
    """Spezialisierte Bot-Admin Commands."""
    def __init__(self, bot: commands.Bot):
        super().__init__(name="admin", description="Spezialisierte Bot-Admin Commands")
        self.bot = bot
    
    def _is_bot_admin(self, interaction: Interaction) -> bool:
        """Prüft, ob der Benutzer ein globaler Bot-Admin (via fester ID) ist. 
           Derzeit wird hier nur die Server-Admin-Berechtigung geprüft."""
        
        # TODO: Hier sollte eine Überprüfung gegen eine harte Coded Bot-Admin-Liste erfolgen
        # Für den Start prüfen wir nur Server-Admin, um die Funktionalität zu testen.
        return interaction.user.guild_permissions.administrator
        
    # --- NEUER COMMAND: /admin setupbearbeiten (Startet die interaktive UI) ---
    @app_commands.command(name="setupbearbeiten", description="Starte die interaktive Bot-Konfiguration (Nur für Bot-Admins).")
    async def interactive_setup(self, interaction: Interaction):
        if not self._is_bot_admin(interaction):
            return await interaction.response.send_message("❌ Nur für Bot-Admins.", ephemeral=True)
            
        view = SetupSelectView(interaction, self, is_admin=True)
        await interaction.response.send_message("Wähle aus, welche Einstellung du bearbeiten möchtest:", view=view, ephemeral=True)

    # COMMAND: /admin config_show (Kopie von setup_commands)
    # --- NEUER COMMAND: /admin setupbearbeiten (Startet die interaktive UI) ---
    @app_commands.command(name="setupbearbeiten", description="Starte die interaktive Bot-Konfiguration (Nur für Bot-Admins).")
    async def interactive_setup(self, interaction: Interaction):
        if not self._is_bot_admin(interaction):
            return await interaction.response.send_message("❌ Nur für Bot-Admins.", ephemeral=True)
            
        view = SetupSelectView(interaction, self, is_admin=True)
        await interaction.response.send_message("Wähle aus, welche Einstellung du bearbeiten möchtest:", view=view, ephemeral=True)

    @app_commands.command(name="config_show", description="Zeigt die aktuelle Bot-Konfiguration (Nur für Bot-Admins).")
    async def show_setup_config(self, interaction: Interaction):
        if not self._is_bot_admin(interaction):
            return await interaction.response.send_message("❌ Nur für Bot-Admins.", ephemeral=True)

        guild_id_str = str(interaction.guild_id)
        config = self.bot.setup_data.get(guild_id_str, {})
        
        embed = await create_setup_embed(interaction, config)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    # --- NEUER COMMAND: /admin setupbearbeiten (Startet die interaktive UI) ---
    @app_commands.command(name="setupbearbeiten", description="Starte die interaktive Bot-Konfiguration (Nur für Bot-Admins).")
    async def interactive_setup(self, interaction: Interaction):
        if not self._is_bot_admin(interaction):
            return await interaction.response.send_message("❌ Nur für Bot-Admins.", ephemeral=True)
            
        view = SetupSelectView(interaction, self, is_admin=True)
        await interaction.response.send_message("Wähle aus, welche Einstellung du bearbeiten möchtest:", view=view, ephemeral=True)

    # COMMAND: /admin setupbearbeiten (Kopie von setup_commands)
    # --- NEUER COMMAND: /admin setupbearbeiten (Startet die interaktive UI) ---
    @app_commands.command(name="setupbearbeiten", description="Starte die interaktive Bot-Konfiguration (Nur für Bot-Admins).")
    async def interactive_setup(self, interaction: Interaction):
        if not self._is_bot_admin(interaction):
            return await interaction.response.send_message("❌ Nur für Bot-Admins.", ephemeral=True)
            
        view = SetupSelectView(interaction, self, is_admin=True)
        await interaction.response.send_message("Wähle aus, welche Einstellung du bearbeiten möchtest:", view=view, ephemeral=True)

            await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)
