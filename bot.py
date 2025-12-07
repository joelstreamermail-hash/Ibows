import discord
from discord import app_commands
import os
from dotenv import load_dotenv
import datetime
import sqlite3
import zoneinfo

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
TARGET_GUILD_ID = int(os.getenv('TARGET_GUILD_ID', '1444022178428358756')) 
VERSION = "V1.0.3" 
TIMEZONE = zoneinfo.ZoneInfo("Europe/Berlin")

def get_db_connection():
    """Stellt die Verbindung zur Datenbank her und gibt sie zurück."""
    conn = sqlite3.connect('warnings.db')
    conn.row_factory = sqlite3.Row 
    return conn

def setup_db():
    """Initialisiert die Datenbank-Tabellen."""
    conn = get_db_connection()
    conn.execute("CREATE TABLE IF NOT EXISTS warnings (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT, guild_id TEXT, moderator TEXT, reason TEXT, timestamp TEXT)")
    conn.execute("CREATE TABLE IF NOT EXISTS settings (guild_id TEXT PRIMARY KEY, mod_role_id TEXT)")
    conn.commit()
    conn.close()
    print("Datenbank 'warnings.db' ist initialisiert.")

def get_mod_role_id(guild_id):
    """Ruft die konfigurierte Mod-Rolle für die Gilde ab."""
    conn = get_db_connection()
    res = conn.execute("SELECT mod_role_id FROM settings WHERE guild_id = ?", (str(guild_id),)).fetchone()
    conn.close()
    return res[0] if res else None

class ModerationBot(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.tree = app_commands.CommandTree(self)
        self.synced = False  
        setup_db() 

    async def on_ready(self):
        await self.wait_until_ready()
        activity = discord.Game(f"Community-Verwaltung | {VERSION}")
        await self.change_presence(activity=activity, status=discord.Status.online)
        if not self.synced:
            try:
                guild = discord.Object(id=TARGET_GUILD_ID)
                self.tree.copy_global_to(guild=guild)
                await self.tree.sync(guild=guild)
                print(f'✅ Slash Commands synchronisiert.')
            except Exception as e:
                print(f'❌ Sync Fehler: {e}')
            self.synced = True
        print(f'Eingeloggt als {self.user} (ID: {self.user.id})')

bot = ModerationBot()

# --- BERECHTIGUNGSPRÜFUNG ---
async def check_mod_role(interaction):
    """Prüft, ob der Benutzer Administrator oder die konfigurierte Mod-Rolle hat."""
    if interaction.user.guild_permissions.administrator:
        return True
    
    rid = get_mod_role_id(interaction.guild_id)
    if not rid: 
        return True 
        
    try:
        mod_role = interaction.guild.get_role(int(rid))
        if mod_role and mod_role in interaction.user.roles:
            return True
    except ValueError:
        pass
        
    await interaction.response.send_message("❌ Fehlende Berechtigung (Du benötigst die konfigurierte Mod-Rolle).", ephemeral=True)
    return False

# --- SLASH COMMANDS ---

@bot.tree.command(name="kick", description="Kickt einen Benutzer.")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Kein Grund"):
    if await check_mod_role(interaction):
        await member.kick(reason=reason)
        await interaction.response.send_message(f'✅ {member.name} gekickt. Grund: {reason}')

@bot.tree.command(name="ban", description="Bannt einen Benutzer.")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Kein Grund"):
    if await check_mod_role(interaction):
        await member.ban(reason=reason)
        await interaction.response.send_message(f'🔨 {member.name} gebannt. Grund: {reason}')

@bot.tree.command(name="warn", description="Verwarnt einen Benutzer.")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    if await check_mod_role(interaction):
        conn = get_db_connection()
        ts = datetime.datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")
        conn.execute("INSERT INTO warnings (user_id, guild_id, moderator, reason, timestamp) VALUES (?,?,?,?,?)", (str(member.id), str(interaction.guild_id), interaction.user.name, reason, ts))
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM warnings WHERE user_id=? AND guild_id=?", (str(member.id), str(interaction.guild_id))).fetchone()[0]
        conn.close()
        await interaction.response.send_message(f'⚠️ {member.name} verwarnt (Warnung #{count}). Grund: {reason}')

setup_group = app_commands.Group(name="setup", description="Bot Einstellungen")
@setup_group.command(name="mod_role")
async def set_mod(interaction: discord.Interaction, role: discord.Role):
    """Setzt die Moderator-Rolle, die Berechtigungen für Moderationsbefehle erhält."""
    if interaction.user.id == interaction.guild.owner_id:
        conn = get_db_connection()
        conn.execute("INSERT OR REPLACE INTO settings (guild_id, mod_role_id) VALUES (?, ?)", (str(interaction.guild_id), str(role.id)))
        conn.commit()
        conn.close()
        await interaction.response.send_message(f"✅ Mod-Rolle erfolgreich auf {role.name} gesetzt.")
    else:
        await interaction.response.send_message("❌ Nur der Server-Eigentümer kann die Mod-Rolle über diesen Befehl setzen.", ephemeral=True)

bot.tree.add_command(setup_group)

if __name__ == "__main__":
    bot.run(TOKEN)
