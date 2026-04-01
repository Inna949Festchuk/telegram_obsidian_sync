#!/usr/bin/env python3
"""
Скрипт для получения API ключей Telegram через SOCKS5 прокси
"""
import asyncio
import os
import sys
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.network.connection.tcpabridged import ConnectionTcpAbridged
import socks

load_dotenv()

async def get_api_keys():
    print("=" * 60)
    print("🔑 Получение API ключей Telegram")
    print("=" * 60)
    print()
    
    api_id = int(os.getenv('API_ID', 2496))
    api_hash = os.getenv('API_HASH', '8da85c0c719b7a0bb007cd60b0d2c667')
    
    # Настройка SOCKS5 прокси - правильный формат
    proxy_host = os.getenv('PROXY_HOST')
    proxy_port = os.getenv('PROXY_PORT')
    
    proxy = None
    if proxy_host and proxy_port:
        proxy_port = int(proxy_port)
        # Правильный формат для Telethon: (socks.SOCKS5, host, port)
        proxy = (socks.SOCKS5, proxy_host, proxy_port)
        print(f"🌐 Использую SOCKS5 прокси: {proxy_host}:{proxy_port}")
    
    # Создаем клиент
    client = TelegramClient(
        'temp_session',
        api_id,
        api_hash,
        connection=ConnectionTcpAbridged,
        proxy=proxy
    )
    
    try:
        print("📱 Подключение к Telegram через прокси...")
        
        # Устанавливаем таймаут
        await asyncio.wait_for(client.connect(), timeout=30)
        
        if not await client.is_user_authorized():
            print("📞 Требуется авторизация")
            
            phone = os.getenv('PHONE_NUMBER')
            if not phone:
                phone = input("Введите номер телефона в международном формате (+79123456789): ")
            
            print("📲 Отправка кода подтверждения...")
            await client.send_code_request(phone)
            
            code = input("Введите код из Telegram: ")
            await client.sign_in(phone, code)
        
        print("✅ Успешная авторизация!")
        
        me = await client.get_me()
        print(f"👤 Авторизован как: {me.first_name} (@{me.username or 'нет username'})")
        
        print("\n🔄 Создаю новое приложение...")
        
        from telethon.tl.functions.account import CreateAppRequest
        
        app = await client(CreateAppRequest(
            title="ObsidianSync",
            short_name="obsidiansync",
            description="Синхронизация постов из Telegram в Obsidian",
            platform="desktop"
        ))
        
        print("\n" + "=" * 60)
        print("✅ ВАШИ API КЛЮЧИ:")
        print("=" * 60)
        print(f"API_ID: {app.app_id}")
        print(f"API_HASH: {app.app_hash}")
        print("=" * 60)
        
        with open('telegram_keys.txt', 'w') as f:
            f.write(f"API_ID={app.app_id}\n")
            f.write(f"API_HASH={app.app_hash}\n")
        
        print("\n💾 Ключи сохранены в файл telegram_keys.txt")
        print("\n📝 Добавьте их в файл .env:")
        print(f'API_ID={app.app_id}')
        print(f'API_HASH={app.app_hash}')
        
    except asyncio.TimeoutError:
        print("\n❌ Таймаут подключения. Проверьте:")
        print("1. Работает ли прокси: curl --socks5 127.0.0.1:1080 https://api.telegram.org")
        print("2. Правильно ли указан порт (1080)")
        print("3. Не блокирует ли фаервол")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        print("\nПроверьте работоспособность прокси:")
        print("docker logs ytdlp_byedpi-byedpi")
    finally:
        await client.disconnect()
        print("\n🔌 Соединение закрыто")

if __name__ == '__main__':
    try:
        asyncio.run(get_api_keys())
    except KeyboardInterrupt:
        print("\n🛑 Прервано пользователем")
        sys.exit(0)