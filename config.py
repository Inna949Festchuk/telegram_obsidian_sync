import os
from dotenv import load_dotenv

load_dotenv()

# Telegram API
API_ID = int(os.getenv('API_ID'))
API_HASH = os.getenv('API_HASH')
PHONE_NUMBER = os.getenv('PHONE_NUMBER')

# Obsidian vault
VAULT_PATH = '/path/to/your/obsidian/vault/telegram_posts/'
# Если хотите сортировать по каналам в подпапках
ORGANIZE_BY_CHANNEL = True

# Настройки синхронизации
CHANNELS = [
    'channel_username_1',  # без @, просто username
    'channel_username_2',
    # или можно использовать ID: -1001234567890
]

# Файл для хранения последних ID сообщений
LAST_IDS_FILE = 'last_ids.json'

# Интервал проверки в секундах (по умолчанию 5 минут)
CHECK_INTERVAL = 300

# Количество последних сообщений для проверки при каждом запуске
MESSAGES_LIMIT = 50

# Форматирование заметок
INCLUDE_DATE = True
INCLUDE_CHANNEL = True
INCLUDE_LINK = True
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Режим работы
# 'once' - однократный импорт истории
# 'watch' - постоянный мониторинг
MODE = 'watch'