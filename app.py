from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import RPCError
import requests
from dotenv import load_dotenv
import os
import asyncio
from threading import Thread
from flask import Flask

load_dotenv()

# Load environment variables
api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
string_session = os.getenv("TG_STRING_SESSION")
channel_username = os.getenv("TG_CHANNEL", "TechUprise_Updates")
n8n_webhook_url = os.getenv("N8N_WEBHOOK_URL", "https://job-workflow-automation.onrender.com/webhook/79a8cb42-a99c-4d6e-858b-2ecd936b7ace")

# Create the Telegram client
client = TelegramClient(StringSession(string_session), api_id, api_hash)

# Flask server for Render keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Telegram bot is alive!", 200

# Telegram message handler
@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    try:
        message = event.message.message or "[Non-text message received]"
        print(f"[TELEGRAM] New message from {channel_username}:\n{message}\n", flush=True)

        response = requests.post(n8n_webhook_url, json={'message': message})
        if response.status_code == 200:
            print(f"[n8n] ✅ Message sent to n8n successfully.", flush=True)
        else:
            print(f"[n8n] ⚠️ Received status code {response.status_code} from n8n.", flush=True)
    except RPCError as e:
        print(f"[TELEGRAM] ❌ RPC Error: {e}", flush=True)
    except Exception as e:
        print(f"[n8n] ❌ Failed to send message to n8n. Error: {e}", flush=True)

# Async bot starter
async def run_bot():
    print("[INFO] Starting Telegram client...", flush=True)
    await client.start()
    print("[INFO] Client started successfully.", flush=True)
    print("[INFO] Listening for new messages...", flush=True)
    await client.run_until_disconnected()

# Wrapper to launch bot in thread
def start_bot():
    asyncio.run(run_bot())

if __name__ == '__main__':
    print("[INFO] Starting the Telegram bot...")
    Thread(target=start_bot).start()
    app.run(host="0.0.0.0", port=10000)
