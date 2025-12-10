# Standard- und Moderationsbefehle
import discord
from discord import app_commands, Embed, Interaction
from discord.ext import commands
class ModerationCommands(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="mod", description="Moderationsbefehle")
        self.bot = bot
    @app_commands.command(name="kick")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: Interaction, member: discord.Member, reason: str = "Kein Grund"):
        if member == interaction.user: return await interaction.response.send_message("❌ Selbstdemontage nicht erlaubt!", ephemeral=True)
        try: await member.kick(reason=reason); await interaction.response.send_message(f"✅ **{member.display_name}** gekickt.")
        except discord.Forbidden: await interaction.response.send_message("❌ Fehlende Berechtigung.", ephemeral=True)
class StandardCommands(app_commands.Group):
    def __init__(self, bot: commands.Bot):
        super().__init__(name="standard", description="Standard Bot Befehle")
        self.bot = bot
    @app_commands.command(name="help")
    async def help_command(self, interaction: Interaction):
        help_embed = Embed(title="🤖 Commands Übersicht", description="Liste der Befehle.", color=discord.Color.blue())
        help_embed.add_field(name="/mod", value="`kick`, `ban`", inline=False)
        await interaction.response.send_message(embed=help_embed, ephemeral=True)
