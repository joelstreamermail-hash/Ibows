# discord-bot-project/Commands/setup_commands.py
from discord.ui import View, Select, Modal, TextInput
import discord
from discord import app_commands, Interaction, Embed, Role, TextChannel, Member
from discord.ext import commands, tasks
from typing import Literal

# --- HILFSFUNKTIONEN (Sollten idealerweise in einer utils.py liegen,
#     aber für die Übersichtlichkeit hier eingefügt) ---

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
    guild = interaction.guild
    
    # 1. Admin Rollen
    admin_roles = get_role_list(guild, config.get("admin_role_ids", []))
    
    # 2. Logging Kanal
    log_channel_id = config.get("log_channel_id")
    log_channel = get_channel_mention(guild, log_channel_id) if log_channel_id else "*(Nicht festgelegt)*"
    
    # 3. Team Panel Daten
    team_panel_roles = config.get("team_panel_roles", [])
    team_panel_channel_id = config.get("team_panel_channel_id")
    team_panel_channel = get_channel_mention(guild, team_panel_channel_id) if team_panel_channel_id else "*(Nicht festgelegt)*"
    
    # Team Mitglieder auflisten
    team_members_str = ""
    for role_id in team_panel_roles:
        role = guild.get_role(role_id)
        if role:
            members_with_role = [m.mention for m in role.members]
            team_members_str += f"\n**{role.name}** ({len(members_with_role)}): "
            team_members_str += ", ".join(members_with_role) if members_with_role else "Keine Mitglieder."
    
    if not team_members_str:
         team_members_str = "*(Keine Team-Rollen für das Panel festgelegt)*"
         
    # --- EMBED ERSTELLEN ---
    setup_embed = Embed(
        title="⚙️ Bot-Konfiguration & Status",
        description=f"Aktueller Setup-Status für **{guild.name}**",
        color=discord.Color.blue()
    )
    
    setup_embed.add_field(
        name="🔒 Admin/Berechtigungs-Einstellungen",
        value=f"**Rollen mit Admin-Berechtigung:**\n{admin_roles}",
        inline=False
    )

    setup_embed.add_field(
        name="📊 Logging-Einstellungen",
        value=f"**Log-Channel:** {log_channel}",
        inline=True
    )
    
    setup_embed.add_field(
        name="👤 Team-Panel-Einstellungen",
        value=f"**Panel-Kanal:** {team_panel_channel}",
        inline=True
    )

    setup_embed.add_field(
        name="👥 Team-Übersicht (Aktuelle Mitglieder)",
        value=team_members_str[:1024], # Kürzung auf max. 1024 Zeichen
        inline=False
    )
    
    return setup_embed

# --- COMMANDS KLASSE ---

class SetupCommands(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="setup", description="Bot Konfiguration und Status")
        self.bot = bot
        self.update_team_panel.start() 
        
    def _is_allowed(self, interaction: Interaction) -> bool:
        """Prüft, ob der Benutzer Admin-Berechtigung hat."""
        if not interaction.guild: return False
        guild_setup = self.bot.setup_data.get(str(interaction.guild_id), {})
        admin_role_ids = guild_setup.get("admin_role_ids", [])
        
        # Server-Admin hat immer Zugriff
        if interaction.user.guild_permissions.administrator: return True
        
        # Mitglieder mit konfigurierter Admin-Rolle haben Zugriff
        if any(role.id in admin_role_ids for role in interaction.user.roles): return True
        
        return False
        
    # ----------------------------------------------------------------------
    # COMMAND: /setup config_show
    # ----------------------------------------------------------------------
    @app_commands.command(name="config_show", description="Zeigt die aktuelle Bot-Konfiguration in einem Embed.")
    async def show_setup_config(self, interaction: Interaction):
        if not self._is_allowed(interaction):
            return await interaction.response.send_message("❌ Du benötigst Admin- oder die konfigurierte Admin-Rolle, um dies zu sehen.", ephemeral=True)

        guild_id_str = str(interaction.guild_id)
        config = self.bot.setup_data.get(guild_id_str, {})
        
        embed = await create_setup_embed(interaction, config)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    # ----------------------------------------------------------------------
    # COMMAND: /setup setupbearbeiten
    # ----------------------------------------------------------------------
            await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)


    @tasks.loop(minutes=4.0)
    async def update_team_panel(self):
        # Logik zum Aktualisieren des Team Panels (wird von der Bot-Instanz aufgerufen)
        pass
