from telethon import TelegramClient, events
import requests

# Telegram API credentials from https://my.telegram.org
api_id = '28920533'
api_hash = '93e710fb3c90ac39d16dd7f3d0cd52eb'

# Phone number used for login (only needed on first run)
phone_number = '+918459615960'

# The public channel to monitor
channel_username = 'TechUprise_Updates'  # Must be public or you're a member

# n8n Webhook URL (replace with your actual webhook URL)
n8n_webhook_url = 'https://job-workflow-automation.onrender.com/webhook/79a8cb42-a99c-4d6e-858b-2ecd936b7ace'

# Create a Telegram client session (session file will be saved as 'session_name.session')
client = TelegramClient('session_name', api_id, api_hash)


@client.on(events.NewMessage(chats=channel_username))
async def handler(event):
    message = event.message.text

    print(f"[TELEGRAM] New message from {channel_username}:\n{message}\n")

    try:
        response = requests.get(n8n_webhook_url, json={'message': message})
        if response.status_code == 200:
            print(f"[n8n] ✅ Message sent to n8n successfully.")
        else:
            print(f"[n8n] ⚠️ Received status code {response.status_code} from n8n.")
    except Exception as e:
        print(f"[n8n] ❌ Failed to send message to n8n. Error: {e}")


def main():
    print("[INFO] Starting Telegram listener...")
    client.start(phone_number)  # Will ask OTP if first run
    print("[INFO] Listening for new messages...")
    client.run_until_disconnected()


if __name__ == '__main__':
    main()
