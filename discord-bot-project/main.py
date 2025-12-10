import os
import threading
import json
from dotenv import load_dotenv
from discord import Intents, Client, app_commands
from Commands.moderation_commands import ModerationCommands
from Commands.setup_commands import SetupCommands as SetupCommandGroup
from Commands.admin_commands import AdminCommands
from flask import Flask, request

# --- Umgebungs- und Konfigurations-Setup ---

load_dotenv() # Lädt Variablen aus der lokalen .env-Datei (nur lokal)

# Variablen global auf Modulebene definieren (Wichtig für Runter und Thread-Zugriff)
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
# Render verwendet den PORT Environment Variable
RENDER_PORT = int(os.getenv("PORT", 10000))
CONFIG_FILE = "bot_config.json"

# Flask App Initialisierung (für den Render Web Service)
app = Flask(__name__)

# --- Persistenz-Funktionen ---
def load_config():
    """Lädt die Konfigurationsdaten aus der JSON-Datei."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
            except json.JSONDecodeError:
                return {}
    return {}

def save_config(data):
    """Speichert die Konfigurationsdaten in die JSON-Datei."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Fehler beim Speichern der Konfiguration: {e}")

# --- Discord Client Definition ---
class MyClient(Client):
    """Der zentrale Discord Bot Client."""
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.setup_data = load_config()
        self.save_config = save_config

    async def on_ready(self):
        # Befehle zur Command Tree hinzufügen
        self.tree.add_command(ModerationCommands(self)) 
        self.tree.add_command(SetupCommandGroup(self))
        self.tree.add_command(AdminCommands(self))
        
        # Commands synchronisieren
        await self.tree.sync() 
        print(f'✅ Bot erfolgreich eingeloggt als {self.user}!')

# Erforderliche Intents definieren
intents = Intents.default()
intents.members = True 
client = MyClient(intents=intents)

# --- Flask Keep-Alive Endpoint ---
@app.route('/')
def home():
    """Der Endpunkt, den Render regelmäßig aufruft, um den Service am Leben zu halten."""
    return "Ibows Discord Bot is running and connected.", 200

# --- Start-Funktionen ---
def run_bot():
    """Startet den Discord Bot Client im Thread."""
    if not DISCORD_BOT_TOKEN:
        print("❌ DISCORD_BOT_TOKEN nicht gefunden. Bot wird nicht gestartet.")
        return
    client.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    # 1. Starte Discord Bot in einem separaten Thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # 2. Starte Flask Server im Hauptthread (für Render)
    print(f"🌍 Starte Flask Webserver auf Port {RENDER_PORT}")
    # Render benötigt host='0.0.0.0'
    app.run(host='0.0.0.0', port=RENDER_PORT)
