# discord-bot-project/Commands/admin_commands.py

import discord
import json
from discord import app_commands, Interaction, Embed
from discord.ext import commands
from typing import Literal
from discord.ui import View, Select, Modal, TextInput # Hinzugefügt für UI

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
        color=discord.Color.dark_red()
    )
    
    setup_embed.add_field(name="🔒 Admin/Berechtigungs-Einstellungen", value=f"**Rollen mit Admin-Berechtigung:**\n{admin_roles}", inline=False)
    setup_embed.add_field(name="📊 Logging-Einstellungen", value=f"**Log-Channel:** {log_channel}", inline=True)
    setup_embed.add_field(name="👤 Team-Panel-Einstellungen", value=f"**Panel-Kanal:** {team_panel_channel}", inline=True)
    setup_embed.add_field(name="👥 Team-Übersicht (Aktuelle Mitglieder)", value=team_members_str[:1024], inline=False)
    
    return setup_embed

# --- UI KLASSEN: Selektoren und Modals ---

class SetupSelectView(View):
    def __init__(self, original_interaction: Interaction, config_group, is_admin: bool):
        super().__init__(timeout=180)
        self.original_interaction = original_interaction
        self.config_group = config_group
        self.is_admin = is_admin
        
        self.add_item(self.create_select_menu())

    def create_select_menu(self):
        options = [
            discord.SelectOption(label="Admin Rollen bearbeiten", value="admin_rollen", description="Rollen festlegen, die den Bot konfigurieren dürfen."),
            discord.SelectOption(label="Logging Kanal festlegen", value="log_kanal", description="Setzt den Kanal für Bot-Logs."),
            discord.SelectOption(label="Team Panel Rollen bearbeiten", value="team_panel_rollen", description="Fügt Rollen für die Anzeige im Team Panel hinzu."),
            discord.SelectOption(label="Team Panel Kanal festlegen", value="team_panel_kanal", description="Setzt den Kanal für das Team Panel."),
        ]
        
        select = Select(placeholder="Wähle eine Konfigurationseinstellung...", options=options)
        select.callback = self.select_callback
        return select

    async def select_callback(self, interaction: Interaction):
        selected_value = interaction.data['values'][0]
        
        await interaction.response.send_modal(ConfigModal(
            self.config_group, 
            selected_value, 
            self.original_interaction.guild_id, 
            self.is_admin
        ))
        
    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True
        try:
            await self.original_interaction.edit_original_response(content="❌ Interaktive Konfiguration abgelaufen.", view=self)
        except discord.NotFound:
            pass


class ConfigModal(Modal):
    def __init__(self, config_group, typ: str, guild_id: int, is_admin: bool):
        super().__init__(title=f"Konfiguriere {typ.replace('_', ' ').title()}")
        self.config_group = config_group
        self.typ = typ
        self.guild_id = guild_id
        self.is_admin = is_admin

        self.id_input = TextInput(
            label="Rollen- oder Kanal-ID",
            placeholder="Gib die ID der Rolle/des Kanals ein",
            required=True
        )
        self.add_item(self.id_input)

    async def on_submit(self, interaction: Interaction):
        target_id = self.id_input.value
        
        await self.config_group.handle_edit(interaction, self.typ, target_id)


# --- HILFSFUNKTION FÜR BEARBEITUNGSLOGIK ---

async def handle_edit_logic(self, interaction: Interaction, typ: str, target_id: str, is_admin_call: bool):
    """Führt die eigentliche Logik zum Hinzufügen/Entfernen von IDs aus."""
    guild_id_str = str(interaction.guild_id)
    if guild_id_str not in self.bot.setup_data: 
        self.bot.setup_data[guild_id_str] = {}
        
    try:
        target_id_int = int(target_id)
        
        context = "(Admin)" if is_admin_call else "(Setup)"
        message = ""

        if typ in ["admin_rollen", "team_panel_rollen"]:
            role = interaction.guild.get_role(target_id_int)
            if not role: return await interaction.response.send_message("❌ Ungültige Rollen-ID.", ephemeral=True)
            
            key = "admin_role_ids" if typ == "admin_rollen" else "team_panel_roles"
            current_list = self.bot.setup_data[guild_id_str].get(key, [])
            
            if target_id_int not in current_list:
                current_list.append(target_id_int)
                message = f"✅ Rolle **{role.name}** zu {typ} hinzugefügt {context}."
            else:
                current_list.remove(target_id_int)
                message = f"✅ Rolle **{role.name}** aus {typ} entfernt {context}."
            
            self.bot.setup_data[guild_id_str][key] = current_list
        
        elif typ in ["log_kanal", "team_panel_kanal"]:
            channel = interaction.guild.get_channel(target_id_int)
            if not isinstance(channel, discord.TextChannel):
                return await interaction.response.send_message("❌ Ungültige Kanal-ID. Es muss ein Text-Kanal sein.", ephemeral=True)
                
            key = "log_channel_id" if typ == "log_kanal" else "team_panel_channel_id"
            self.bot.setup_data[guild_id_str][key] = target_id_int
            message = f"✅ {typ.replace('_', ' ').capitalize()} auf {channel.mention} gesetzt {context}."
        else:
            message = "❌ Unbekannter Typ."

        self.bot.save_config(self.bot.setup_data) 
        await interaction.response.send_message(message, ephemeral=True)
        
    except ValueError: 
        await interaction.response.send_message("❌ Ungültige ID. Bitte nur Ziffern eingeben.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Fehler beim Speichern: {e}", ephemeral=True)


# --- COMMANDS KLASSE ---

class AdminCommands(app_commands.Group):
    """Spezialisierte Bot-Admin Commands."""
    def __init__(self, bot: commands.Bot):
        super().__init__(name="admin", description="Spezialisierte Bot-Admin Commands")
        self.bot = bot
    
    def _is_bot_admin(self, interaction: Interaction) -> bool:
        """Prüft, ob der Benutzer ein globaler Bot-Admin (via fester ID) oder Server-Admin ist."""
        # TODO: Hier sollte eine Überprüfung gegen eine harte Coded Bot-Admin-Liste erfolgen
        return interaction.user.guild_permissions.administrator
        
    # ----------------------------------------------------------------------
    # COMMAND: /admin config_show
    # ----------------------------------------------------------------------
    @app_commands.command(name="config_show", description="Zeigt die aktuelle Bot-Konfiguration (Nur für Bot-Admins).")
    async def show_setup_config(self, interaction: Interaction):
        if not self._is_bot_admin(interaction):
            return await interaction.response.send_message("❌ Nur für Bot-Admins.", ephemeral=True)

        guild_id_str = str(interaction.guild_id)
        config = self.bot.setup_data.get(guild_id_str, {})
        
        embed = await create_setup_embed(interaction, config)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    # ----------------------------------------------------------------------
    # COMMAND: /admin setupbearbeiten (Startet die interaktive UI)
    # ----------------------------------------------------------------------
    @app_commands.command(name="setupbearbeiten", description="Starte die interaktive Bot-Konfiguration (Nur für Bot-Admins).")
    async def interactive_setup(self, interaction: Interaction):
        if not self._is_bot_admin(interaction):
            return await interaction.response.send_message("❌ Nur für Bot-Admins.", ephemeral=True)
            
        view = SetupSelectView(interaction, self, is_admin=True)
        await interaction.response.send_message("Wähle aus, welche Einstellung du bearbeiten möchtest:", view=view, ephemeral=True)
        
    # ----------------------------------------------------------------------
    # METHODE: Bearbeitungslogik (Wird vom Modal aufgerufen)
    # ----------------------------------------------------------------------
    async def handle_edit(self, interaction: Interaction, typ: str, target_id: str):
        await handle_edit_logic(self, interaction, typ, target_id, is_admin_call=True)

