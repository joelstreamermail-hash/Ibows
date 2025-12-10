# main.py (Auszug mit den Korrekturen)
import os
import threading
import json
from dotenv import load_dotenv
from discord import Intents, Client, app_commands
from Commands.standard_commands import StandardCommands, ModerationCommands
from Commands.setup_commands import SetupCommands
from Commands.admin_commands import AdminCommands
from flask import Flask, request # <--- WICHTIG: Flask muss importiert sein

# ... (load_dotenv, load_config, save_config Funktionen bleiben gleich) ...

# ----------------------------------------------
# 1. KORREKTUR: FLASK APP HIER INITIALISIEREN
# Flask-App für den Render Web Service
app = Flask(__name__) # <--- HIER MUSS 'app' DEFINIERT WERDEN!

@app.route('/')
def home():
    # Render ruft diesen Endpunkt auf, um den Bot am Leben zu halten (Keep-Alive)
    return "Discord Bot is running and connected."
# ----------------------------------------------

# Discord Bot Client initialisieren (Klasse MyClient)
class MyClient(Client):
    # ... (Rest der Klasse bleibt gleich) ...
    pass
    
# Erforderliche Intents definieren
intents = Intents.default()
intents.members = True 
client = MyClient(intents=intents)

# Funktion zum Starten des Bots
def run_bot():
    client.run(DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    # Starte Discord Bot in einem separaten Thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Starte Flask Server im Hauptthread
    # NameError wird behoben, da 'app' nun definiert ist.
    app.run(host='0.0.0.0', port=os.getenv('PORT', 10000))