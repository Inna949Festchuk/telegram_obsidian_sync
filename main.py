#!/usr/bin/env python3
import asyncio
import sys
import logging
from telethon import TelegramClient

from config import *
from note_formatter import NoteFormatter
from sync_manager import SyncManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def main():
    # Создаем клиент Telegram
    client = TelegramClient('telegram_session', API_ID, API_HASH)
    
    try:
        # Авторизация
        await client.start(phone=PHONE_NUMBER)
        logger.info("✅ Успешная авторизация в Telegram")
        
        # Получаем информацию о пользователе
        me = await client.get_me()
        logger.info(f"👤 Авторизован как: {me.first_name} (@{me.username})")
        
        # Создаем компоненты
        config = {
            'VAULT_PATH': VAULT_PATH,
            'ORGANIZE_BY_CHANNEL': ORGANIZE_BY_CHANNEL,
            'INCLUDE_DATE': INCLUDE_DATE,
            'INCLUDE_CHANNEL': INCLUDE_CHANNEL,
            'INCLUDE_LINK': INCLUDE_LINK,
            'DATE_FORMAT': DATE_FORMAT,
            'LAST_IDS_FILE': LAST_IDS_FILE,
            'CHANNELS': CHANNELS,
            'MESSAGES_LIMIT': MESSAGES_LIMIT,
            'CHECK_INTERVAL': CHECK_INTERVAL
        }
        
        formatter = NoteFormatter(config)
        sync_manager = SyncManager(client, config, formatter)
        
        # Проверяем существование папки Obsidian
        import os
        if not os.path.exists(VAULT_PATH):
            logger.warning(f"⚠️ Папка {VAULT_PATH} не существует. Создаю...")
            os.makedirs(VAULT_PATH, exist_ok=True)
            logger.info(f"✅ Папка создана: {VAULT_PATH}")
        
        # Запускаем в выбранном режиме
        if MODE == 'once':
            # Однократная синхронизация
            await sync_manager.sync_all_channels()
            
        elif MODE == 'watch':
            # Постоянный мониторинг
            await sync_manager.start_watching()
            
        else:
            logger.error(f"❌ Неизвестный режим: {MODE}. Используйте 'once' или 'watch'")
            
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        raise
    finally:
        await client.disconnect()
        logger.info("🔌 Отключено от Telegram")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Остановлено пользователем")
        sys.exit(0)