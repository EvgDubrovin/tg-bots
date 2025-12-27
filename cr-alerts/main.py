import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import MemorySession
from dotenv import load_dotenv

load_dotenv()

api_id = int(os.getenv('API_ID'))
api_hash = os.getenv('API_HASH')
bot_token = os.getenv('BOT_TOKEN')
phone = os.getenv('PHONE')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
TOPIC_ID = int(os.getenv('TOPIC_ID'))

async def monitor_topic():
    client = TelegramClient(MemorySession(), api_id, api_hash)
    bot_client = TelegramClient(MemorySession(), api_id, api_hash)
    
    try:
        await client.start(phone=phone)
        await bot_client.start(bot_token=bot_token)

        channel = await client.get_entity(CHANNEL_ID)
        me = await client.get_me()

        print(f"📊 Мониторю канал: {channel.title}")
        print(f"🎯 Топик ID: {TOPIC_ID}")

        last_id = 0
        first_run = True

        print("🚀 Начинаю мониторинг...")

        while True:
            try:
                messages = await client.get_messages(channel, limit=30)
                
                topic_messages = [
                    msg for msg in messages
                    if hasattr(msg, 'reply_to') and msg.reply_to
                    and hasattr(msg.reply_to, 'reply_to_top_id')
                    and msg.reply_to.reply_to_top_id == TOPIC_ID
                ]

                if topic_messages:
                    newest_msg = max(topic_messages, key=lambda x: x.id)

                    if first_run:
                        print(f"📌 Начальное ID: {newest_msg.id}")
                        last_id = newest_msg.id
                        first_run = False
                    elif newest_msg.id > last_id:
                        print(f"📨 Новый сигнал ID: {newest_msg.id}")
                        
                        await bot_client.send_message(
                            int(me.id),
                            f"📢 Новый торговый сигнал:\n\n{newest_msg.text}"
                        )
                        
                        last_id = newest_msg.id
                
                await asyncio.sleep(15)
                
            except Exception as e:
                print(f"🚫 Ошибка: {e}")
                await asyncio.sleep(60)

    except Exception as e:
        print(f"💀 Критическая ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(monitor_topic())