import os
import asyncio
import logging
from telethon import TelegramClient, events
import aiohttp
import json
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramChannelMonitor:
    def __init__(self):
        # Load configuration from environment variables for security
        self.api_id = os.getenv('TELEGRAM_API_ID', '28920533')
        self.api_hash = os.getenv('TELEGRAM_API_HASH', '93e710fb3c90ac39d16dd7f3d0cd52eb')
        self.phone_number = os.getenv('TELEGRAM_PHONE', '+918459615960')
        self.channel_username = os.getenv('TELEGRAM_CHANNEL', 'adobe_exam_solutions')
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL', 
                                       'https://job-workflow-automation.onrender.com/webhook/79a8cb42-a99c-4d6e-858b-2ecd936b7ace')
        
        # Create Telegram client
        self.client = TelegramClient('session_name', self.api_id, self.api_hash)
        
        # Setup event handler
        self.client.on(events.NewMessage(chats=self.channel_username))(self.handle_new_message)
    
    async def handle_new_message(self, event):
        """Handle new messages from the monitored channel"""
        try:
            message_text = event.message.text or ""
            message_id = event.message.id
            date = event.message.date
            sender_id = event.message.sender_id
            
            # Create comprehensive message data
            message_data = {
                'message_id': message_id,
                'message': message_text,
                'date': date.isoformat() if date else None,
                'sender_id': sender_id,
                'channel': self.channel_username,
                'has_media': bool(event.message.media),
                'media_type': self._get_media_type(event.message.media) if event.message.media else None
            }
            
            logger.info(f"New message from {self.channel_username} (ID: {message_id})")
            logger.info(f"Message preview: {message_text[:100]}...")
            
            # Send to n8n webhook
            await self.send_to_n8n(message_data)
            
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    def _get_media_type(self, media) -> Optional[str]:
        """Determine the type of media in the message"""
        if not media:
            return None
        
        media_type = type(media).__name__
        return media_type.replace('MessageMedia', '').lower()
    
    async def send_to_n8n(self, message_data: dict):
        """Send message data to n8n webhook"""
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.n8n_webhook_url,
                    json=message_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        logger.info("✅ Message sent to n8n successfully")
                    else:
                        response_text = await response.text()
                        logger.warning(f"⚠️ n8n returned status {response.status}: {response_text}")
                        
        except asyncio.TimeoutError:
            logger.error("❌ Timeout while sending to n8n webhook")
        except Exception as e:
            logger.error(f"❌ Failed to send message to n8n: {e}")
    
    async def start(self):
        """Start the Telegram client and begin monitoring"""
        try:
            logger.info("Starting Telegram client...")
            await self.client.start(phone=self.phone_number)
            
            # Get channel info
            try:
                channel_entity = await self.client.get_entity(self.channel_username)
                logger.info(f"Successfully connected to channel: {channel_entity.title}")
            except Exception as e:
                logger.error(f"Could not access channel {self.channel_username}: {e}")
                return
            
            logger.info(f"Monitoring channel: {self.channel_username}")
            logger.info("Bot is running. Press Ctrl+C to stop.")
            
            # Keep the client running
            await self.client.run_until_disconnected()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt signal. Shutting down...")
        except Exception as e:
            logger.error(f"Error starting client: {e}")
        finally:
            await self.client.disconnect()
            logger.info("Telegram client disconnected")

def main():
    """Main function to run the monitor"""
    monitor = TelegramChannelMonitor()
    
    try:
        asyncio.run(monitor.start())
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == '__main__':
    main()