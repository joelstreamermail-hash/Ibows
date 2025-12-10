import discord
from discord.ext import commands
import os
import json
import asyncio
from flask import Flask

# Importiere Commands mit Aliasen, um Namenskollisionen zu vermeiden
from Commands.setup_commands import SetupCommands as SetupCommandGroup
from Commands.admin_commands import AdminCommands as AdminCommandGroup

# --- KONFIGURATION ---
CONFIG_FILE = 'setup_data.json'
TOKEN = os.getenv('DISCORD_BOT_TOKEN') # Empfohlen: Nutze Umgebungsvariablen
if not TOKEN:
    print("FATAL: DISCORD_BOT_TOKEN Umgebungsvariable nicht gesetzt!")
    # TOKEN = "DEIN_BOT_TOKEN_FALLBACK" # Fügen Sie hier einen Fallback ein, falls nötig

# Lade Konfigurationsdaten
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

# Speichere Konfigurationsdaten
def save_config(data):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# --- FLASK WEB SERVER (für Render) ---
app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot is running!'

def run_flask():
    port = int(os.environ.get('PORT', 10000))
    print(f"🌍 Starte Flask Webserver auf Port {port}")
    # Nutze 0.0.0.0, um auf Render erreichbar zu sein
    app.run(host='0.0.0.0', port=port)

# --- DISCORD BOT CLIENT ---

class MyClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(command_prefix="!", intents=intents)
        self.tree = discord.app_commands.CommandTree(self)
        self.setup_data = load_config()

    def save_config(self, data):
        """Methode zum Speichern der Konfiguration, verfügbar für alle Command-Klassen."""
        save_config(data)

    async def setup_hook(self):
        # Lade Command-Gruppen hier, bevor der Bot verbunden wird
        self.tree.add_command(SetupCommandGroup(self))
        self.tree.add_command(AdminCommandGroup(self))
        
        # Stelle sicher, dass die tasks korrekt gestartet werden, falls sie in den Command-Klassen definiert sind
        for extension in self.cogs.values():
            if hasattr(extension, 'update_team_panel') and isinstance(extension.update_team_panel, discord.ext.tasks.Loop):
                extension.update_team_panel.start()


    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('Commands cleared and synchronized globally.')
        
        # **WICHTIG:** Befehl zum Löschen aller alten Commands (EINMALIG AUSFÜHREN)
        # Nachdem die Duplikate behoben sind, MUSS diese Zeile auskommentiert/gelöscht werden.
        await self.tree.clear_commands(guild=None) 
        
        # Synchronsiert alle Commands
        await self.tree.sync() 

# Intents definieren
intents = discord.Intents.default()
intents.members = True # Wichtig für Team Panel und Rollenprüfung
intents.message_content = True # Für Bot-Commands und Logging (falls benötigt)

client = MyClient(intents=intents)

# --- START BOT UND FLASK ---
if __name__ == '__main__':
    # Flask in einem separaten Thread starten
    import threading
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Bot starten
    if TOKEN:
        client.run(TOKEN)
    else:
        print("Bot-Start abgebrochen, da kein Token gefunden wurde.")
