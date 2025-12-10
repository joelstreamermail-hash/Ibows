# discord-bot-project/Commands/moderation_commands.py
import discord
from discord import app_commands, Embed, Interaction, Member
from discord.ext import commands
from typing import Optional, Literal
from datetime import timedelta

# Hilfsfunktion, um die Zeitdauer in Sekunden zu konvertieren
def parse_time(unit: str, amount: int) -> timedelta:
    if unit == "Minuten":
        return timedelta(minutes=amount)
    elif unit == "Stunden":
        return timedelta(hours=amount)
    elif unit == "Tage":
        return timedelta(days=amount)
    return timedelta(minutes=1) 

class ModerationCommands(app_commands.Group):
    """Gruppe für alle Moderations-Slash Commands."""
    def __init__(self, bot: commands.Bot):
        super().__init__(name="mod", description="Alle Moderationsbefehle")
        self.bot = bot

    # --- KICK ---
    @app_commands.command(name="kick", description="Kickt einen Benutzer vom Server.")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: Interaction, member: Member, reason: Optional[str] = "Kein Grund angegeben"):
        if member == interaction.user:
            return await interaction.response.send_message("❌ Du kannst dich nicht selbst kicken.", ephemeral=True)
        try:
            await member.kick(reason=reason)
            await interaction.response.send_message(f"✅ **{member.display_name}** wurde gekickt. Grund: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Fehlende Berechtigung.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Fehler: {e}", ephemeral=True)

    # --- BAN ---
    @app_commands.command(name="ban", description="Bannt einen Benutzer permanent vom Server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: Interaction, member: Member, reason: Optional[str] = "Kein Grund angegeben"):
        if member == interaction.user:
            return await interaction.response.send_message("❌ Du kannst dich nicht selbst bannen.", ephemeral=True)
        try:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"✅ **{member.display_name}** wurde gebannt. Grund: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Fehlende Berechtigung.", ephemeral=True)

    # --- UNBAN/ENTBANN ---
    @app_commands.command(name="entbann", description="Entbannt einen Benutzer mittels seiner ID.")
    @app_commands.default_permissions(ban_members=True)
    async def entbann(self, interaction: Interaction, user_id: str):
        try:
            user = discord.Object(id=int(user_id))
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"✅ Benutzer mit der ID **{user_id}** wurde entbannt.", ephemeral=False)
        except (ValueError, discord.NotFound, discord.Forbidden):
             await interaction.response.send_message("❌ Fehler beim Entbannen (ID falsch, Benutzer nicht gebannt oder fehlende Berechtigung).", ephemeral=True)

    # --- TIMEOUT/MUTE ---
    @app_commands.command(name="timeout", description="Versetzt einen Benutzer für eine bestimmte Zeit in den Timeout.")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_user(self, interaction: Interaction, member: Member,
                           amount: app_commands.Range[int, 1, 60],
                           unit: Literal["Minuten", "Stunden", "Tage"],
                           reason: Optional[str] = "Kein Grund angegeben"):
        
        duration = parse_time(unit, amount)
        if duration > timedelta(days=28):
            return await interaction.response.send_message("❌ Max. Timeout-Dauer ist 28 Tage.", ephemeral=True)
            
        try:
            await member.timeout(duration, reason=reason)
            await interaction.response.send_message(f"✅ **{member.display_name}** für **{amount} {unit}** in Timeout. Grund: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Fehlende Berechtigung.", ephemeral=True)
        
    @app_commands.command(name="mute", description="Siehe /mod timeout.")
    @app_commands.default_permissions(moderate_members=True)
    async def mute_alias(self, interaction: Interaction, member: Member,
                           amount: app_commands.Range[int, 1, 60],
                           unit: Literal["Minuten", "Stunden", "Tage"],
                           reason: Optional[str] = "Kein Grund angegeben"):
        await self.timeout_user(interaction, member, amount, unit, reason)

    # --- TIMEOUT ENDE/UNMUTE ---
    @app_commands.command(name="timeoutende", description="Hebt den Timeout eines Benutzers auf.")
    @app_commands.default_permissions(moderate_members=True)
    async def timeout_end(self, interaction: Interaction, member: Member, reason: Optional[str] = "Timeout aufgehoben"):
        if member.timed_out_until is None:
            return await interaction.response.send_message(f"❌ **{member.display_name}** hat keinen aktiven Timeout.", ephemeral=True)
            
        try:
            await member.timeout(None, reason=reason)
            await interaction.response.send_message(f"✅ Timeout für **{member.display_name}** wurde aufgehoben. Grund: {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Fehlende Berechtigung.", ephemeral=True)

    @app_commands.command(name="entmute", description="Siehe /mod timeoutende.")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute_alias(self, interaction: Interaction, member: Member, reason: Optional[str] = "Timeout aufgehoben"):
        await self.timeout_end(interaction, member, reason)
