from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import RPCError
import requests
from dotenv import load_dotenv
import os

load_dotenv()

api_id = int(os.getenv("TG_API_ID"))
api_hash = os.getenv("TG_API_HASH")
string_session = os.getenv("TG_STRING_SESSION")

channel_username = 'adobe_exam_solutions'
n8n_webhook_url = 'https://job-workflow-automation.onrender.com/webhook/79a8cb42-a99c-4d6e-858b-2ecd936b7ace'

client = TelegramClient(StringSession(string_session), api_id, api_hash)


@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    try:
        message = event.message.message or "[Non-text message received]"
        print(f"[TELEGRAM] New message from {channel_username}:\n{message}\n")

        response = requests.get(n8n_webhook_url, json={'message': message})
        if response.status_code == 200:
            print(f"[n8n] ✅ Message sent to n8n successfully.")
        else:
            print(f"[n8n] ⚠️ Received status code {response.status_code} from n8n.")
    except RPCError as e:
        print(f"[TELEGRAM] ❌ RPC Error: {e}")
    except Exception as e:
        print(f"[n8n] ❌ Failed to send message to n8n. Error: {e}")

import sys

def main():
    print("[INFO] Initializing Telegram client...", flush=True)
    try:
        client.start()
        print("[INFO] Client started successfully.", flush=True)
    except Exception as e:
        print(f"[ERROR] Failed to start client: {e}", flush=True)
        sys.exit(1)

    print("[INFO] Listening for new messages...", flush=True)
    client.run_until_disconnected()


if __name__ == '__main__':
    print("[INFO] Starting the Telegram bot...")
    main()
