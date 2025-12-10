# main.py (WIE ZUVOR MIT JSON LOGIK)
import os, threading, json
from dotenv import load_dotenv
from discord import Intents, Client, app_commands
from Commands.standard_commands import StandardCommands, ModerationCommands
from Commands.setup_commands import SetupCommands
from Commands.admin_commands import AdminCommands
from flask import Flask, request

load_dotenv()
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
RENDER_SECRET_KEY = os.getenv("RENDER_SECRET_KEY")
CONFIG_FILE = "bot_config.json" 

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try: return json.load(f) if isinstance(json.load(f), dict) else {}
            except json.JSONDecodeError: return {}
    return {}
def save_config(data):
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        print(f"❌ Fehler beim Speichern: {e}")
class MyClient(Client):
    def __init__(self, *, intents: Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.setup_data = load_config()
        self.save_config = save_config
    async def on_ready(self):
        self.tree.add_command(StandardCommands(self))
        self.tree.add_command(ModerationCommands(self)) 
        self.tree.add_command(SetupCommands(self))
        self.tree.add_command(AdminCommands(self))
        await self.tree.sync() 
        print(f'Eingeloggt als {self.user}')
intents = Intents.default()
intents.members = True 
client = MyClient(intents=intents)
def run_bot(): client.run(DISCORD_BOT_TOKEN)
if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    app.run(host='0.0.0.0', port=os.getenv('PORT', 10000))
