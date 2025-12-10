# Setup Commands mit Persistenz
import discord
from discord import app_commands, Interaction, Embed, Role, TextChannel
from discord.ext import commands, tasks
from typing import Literal
class SetupCommands(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="setup", description="Bot Konfiguration")
        self.bot = bot
        self.update_team_panel.start() 
    def _is_allowed(self, interaction: Interaction) -> bool:
        if not interaction.guild: return False
        guild_setup = self.bot.setup_data.get(str(interaction.guild_id), {})
        admin_role_ids = guild_setup.get("admin_role_ids", [])
        if interaction.user.guild_permissions.administrator: return True
        if any(role.id in admin_role_ids for role in interaction.user.roles): return True
        return False
    @app_commands.command(name="setupbearbeiten")
    async def edit_setup_command(self, interaction: Interaction, typ: Literal["admin_rollen", "log_kanal"], target_id: str):
        if not self._is_allowed(interaction): return await interaction.response.send_message("❌ Keine Berechtigung.", ephemeral=True)
        guild_id_str = str(interaction.guild_id)
        if guild_id_str not in self.bot.setup_data: self.bot.setup_data[guild_id_str] = {}
        try:
            target_id_int = int(target_id)
            if typ == "admin_rollen":
                role = interaction.guild.get_role(target_id_int)
                if not role: return await interaction.response.send_message("❌ Ungültige Rollen-ID.", ephemeral=True)
                current_roles = self.bot.setup_data[guild_id_str].get("admin_role_ids", [])
                if target_id_int not in current_roles:
                    current_roles.append(target_id_int)
                    message = f"✅ Rolle {role.name} hinzugefügt."
                else:
                    current_roles.remove(target_id_int)
                    message = f"✅ Rolle {role.name} entfernt."
                self.bot.setup_data[guild_id_str]["admin_role_ids"] = current_roles
            # SPEICHERUNG
            self.bot.save_config(self.bot.setup_data) 
            await interaction.response.send_message(message, ephemeral=True)
        except ValueError: await interaction.response.send_message("❌ Ungültige ID.", ephemeral=True)
    @tasks.loop(minutes=4.0)
    async def update_team_panel(self):
        # Aktualisiert alle 4 Minuten
        pass # Logik ist hier weggelassen, aber im finalen Code aktiv.
