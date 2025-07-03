from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from dotenv import load_dotenv
import os

load_dotenv()

api_id = os.getenv("TG_API_ID")
api_hash = os.getenv("TG_API_HASH")

with TelegramClient(StringSession(), api_id, api_hash) as client:
    print(client.session.save())
