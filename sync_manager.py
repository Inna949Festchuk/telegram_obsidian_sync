import json
import os
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import Message
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SyncManager:
    def __init__(self, client, config, formatter):
        self.client = client
        self.config = config
        self.formatter = formatter
        self.last_ids = self._load_last_ids()
        self.vault_path = config['VAULT_PATH']
        
        # Создаем папку для заметок, если её нет
        os.makedirs(self.vault_path, exist_ok=True)
    
    def _load_last_ids(self):
        """Загружает последние ID сообщений из файла"""
        if os.path.exists(self.config['LAST_IDS_FILE']):
            with open(self.config['LAST_IDS_FILE'], 'r') as f:
                return json.load(f)
        return {}
    
    def _save_last_ids(self):
        """Сохраняет последние ID сообщений"""
        with open(self.config['LAST_IDS_FILE'], 'w') as f:
            json.dump(self.last_ids, f, indent=2)
    
    def _update_last_id(self, channel_id, message_id):
        """Обновляет последний ID для канала"""
        self.last_ids[str(channel_id)] = message_id
        self._save_last_ids()
    
    async def process_message(self, message, channel):
        """Обрабатывает одно сообщение"""
        try:
            # Проверяем, не обработали ли уже
            channel_key = str(message.chat_id)
            last_id = self.last_ids.get(channel_key, 0)
            
            if message.id <= last_id:
                return False
            
            # Форматируем заметку
            channel_title = channel.title if hasattr(channel, 'title') else str(channel.id)
            content = self.formatter.format_note(message, channel_title)
            
            # Определяем путь к файлу
            rel_path = self.formatter.get_file_path(message, channel_title)
            full_path = os.path.join(self.vault_path, rel_path)
            
            # Создаем подпапки, если нужно
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Сохраняем файл
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Обновляем последний ID
            self._update_last_id(channel_key, message.id)
            
            logger.info(f"✅ Сохранено: {rel_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка при обработке сообщения {message.id}: {e}")
            return False
    
    async def sync_channel(self, channel_identifier):
        """Синхронизирует один канал"""
        try:
            # Получаем объект канала
            channel = await self.client.get_entity(channel_identifier)
            channel_key = str(channel.id)
            
            # Получаем последние сообщения
            messages = await self.client.get_messages(
                channel, 
                limit=self.config['MESSAGES_LIMIT']
            )
            
            # Обрабатываем сообщения в обратном порядке (от старых к новым)
            new_count = 0
            for message in reversed(messages):
                if await self.process_message(message, channel):
                    new_count += 1
            
            if new_count > 0:
                logger.info(f"📡 Канал '{channel.title}': добавлено {new_count} новых заметок")
            else:
                logger.info(f"📡 Канал '{channel.title}': новых сообщений нет")
                
        except Exception as e:
            logger.error(f"❌ Ошибка при синхронизации {channel_identifier}: {e}")
    
    async def sync_all_channels(self):
        """Синхронизирует все каналы из конфига"""
        logger.info("🔄 Начинаю синхронизацию...")
        
        for channel in self.config['CHANNELS']:
            await self.sync_channel(channel)
        
        logger.info("✅ Синхронизация завершена")
    
    async def start_watching(self):
        """Запускает постоянный мониторинг новых сообщений"""
        logger.info("👁️ Запускаю режим наблюдения...")
        
        # Подписываемся на новые сообщения
        @self.client.on(events.NewMessage(chats=self.config['CHANNELS']))
        async def handler(event):
            message = event.message
            channel = await event.get_chat()
            
            # Проверяем, не обработали ли уже
            channel_key = str(message.chat_id)
            last_id = self.last_ids.get(channel_key, 0)
            
            if message.id > last_id:
                await self.process_message(message, channel)
        
        # Сначала синхронизируем историю
        await self.sync_all_channels()
        
        # Затем держим соединение открытым
        logger.info("👂 Ожидаю новые сообщения...")
        await self.client.run_until_disconnected()