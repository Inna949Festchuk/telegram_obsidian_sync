# CLOUD.md — Техническая спецификация для команды AI-агентов

## Telegram to Obsidian Converter

**Версия документа:** 1.0  
**Дата:** Апрель 2026  
**Статус:** Готов к реализации  
**Репозиторий:** github.com/Inna949Festchuk/telegram_obsidian_sync

---

## 1. Обзор проекта

### 1.1 Назначение

Приложение для конвертации экспорта данных Telegram Desktop в формат заметок Obsidian с полной поддержкой медиафайлов, форматирования текста, метаданных и интеграции с AI-поиском.

### 1.2 Целевая аудитория

- Пользователи Obsidian, желающие импортировать историю Telegram
- Исследователи и аналитики данных
- Разработчики, создающие личные базы знаний

### 1.3 Ключевые возможности

| Функция | Описание | Приоритет |
|---------|----------|-----------|
| Парсинг JSON | Чтение экспорта Telegram result.json | P0 |
| Конвертация в Markdown | Преобразование сообщений в формат Obsidian | P0 |
| Копирование медиа | Фото, видео, стикеры, документы в папку с заметкой | P0 |
| Группировка по дням | Объединение сообщений за день в один файл | P0 |
| Frontmatter | YAML-метаданные для каждой заметки | P1 |
| Контакты | Создание заметок для контактов из экспорта | P1 |
| Индексный файл | Главная страница со статистикой и навигацией | P1 |
| Индексация медиа | Генерация patch.txt для поиска файлов | P0 |
| AI-интеграция | Подключение Ollama и онлайн LLM для поиска | P2 |
| CLI | Интерфейс командной строки | P1 |

---

## 2. Архитектура системы

### 2.1 Компоненты

```
┌─────────────────────────────────────────────────────────────┐
│                    Пользовательский интерфейс                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   CLI       │  │   GUI       │  │   Obsidian Plugin   │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Конвертер (Core)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ JSON Parser │  │ Media Copy  │  │ Markdown Generator  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    AI Модуль (Optional)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Ollama    │  │  Online API │  │   Embeddings        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    Хранилище                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Obsidian   │  │   patch.txt │  │   Media Cache       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Поток данных

```
Telegram Export JSON
        │
        ▼
┌───────────────────┐
│  Загрузка JSON    │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Генерация        │
│  patch.txt        │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Индексация       │
│  медиафайлов      │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Обработка чатов  │
│  (группировка)    │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Конвертация      │
│  в Markdown       │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Копирование      │
│  медиафайлов      │
└───────────────────┘
        │
        ▼
┌───────────────────┐
│  Создание индекса │
│  и контактов      │
└───────────────────┘
        │
        ▼
Obsidian Vault
```

### 2.3 Структура проекта

```
telegram_obsidian_sync/
├── README.md                    # Документация пользователя
├── CLOUD.md                     # Этот документ (спецификация)
├── requirements.txt             # Зависимости Python
├── .env.example                 # Шаблон конфигурации
├── .gitignore                   # Игнорируемые файлы
├── telegram_to_obsidian.py      # Основной скрипт конвертации
├── cli.py                       # CLI интерфейс (опционально)
├── ai_integration/              # Модуль AI-интеграции
│   ├── __init__.py
│   ├── ollama_client.py         # Клиент для Ollama
│   ├── online_clients.py        # Клиенты для онлайн API
│   └── embeddings.py            # Генерация эмбеддингов
├── tests/                       # Тесты
│   ├── __init__.py
│   ├── test_converter.py
│   └── test_ai.py
└── docs/                        # Дополнительная документация
    ├── setup_guide.md
    ├── ai_setup.md
    └── troubleshooting.md
```

---

## 3. Входные данные

### 3.1 Формат экспорта Telegram

**Источник:** Telegram Desktop → Настройки → Продвинутые → Экспорт данных

**Структура экспорта:**
```
DataExport_YYYY-MM-DD/
├── result.json              # Метаданные (обязательно)
├── chats/
│   ├── chat_001/
│   │   ├── messages.html
│   │   ├── messages2.html
│   │   └── photos/
│   └── chat_002/
│       └── ...
├── profile_pictures/
├── css/
├── js/
└── export_results.html
```

### 3.2 Формат result.json

```json
{
  "chats": {
    "list": [
      {
        "id": 123456,
        "type": "channel",
        "name": "Название канала",
        "messages": [
          {
            "id": 1000,
            "type": "message",
            "date": "2024-01-15T10:30:00",
            "date_unixtime": "1705315800",
            "from": "Автор",
            "from_id": "channel1039626561",
            "photo": "chats/chat_003/photos/photo_1.jpg",
            "photo_file_size": 65889,
            "width": 1280,
            "height": 904,
            "text": "Текст сообщения",
            "text_entities": [
              {"type": "bold", "text": "жирный"},
              {"type": "italic", "text": "курсив"},
              {"type": "link", "href": "https://..."}
            ],
            "reactions": [
              {"type": "emoji", "count": 9, "emoji": "👍"}
            ]
          }
        ]
      }
    ]
  },
  "contacts": {
    "list": [
      {
        "first_name": "Иван",
        "last_name": "Петров",
        "phone_number": "+79991234567",
        "date": "2023-01-15"
      }
    ]
  },
  "profile_pictures": [
    {
      "photo": "profile_pictures/photo_1.jpg"
    }
  ]
}
```

### 3.3 Типы чатов

| Тип | Описание | Пример |
|-----|----------|--------|
| `saved_messages` | Сохранённые сообщения | Saved Messages |
| `personal_chat` | Личная переписка | Иван Петров |
| `group` | Группа | Работа |
| `supergroup` | Супергруппа | Большой чат |
| `channel` | Канал | Новости |
| `bot_chat` | Бот | @BotFather |

### 3.4 Типы медиа в JSON

| Ключ JSON | Тип медиа | Пример пути |
|-----------|-----------|-------------|
| `photo` | Фотография | `chats/chat_003/photos/photo_1.jpg` |
| `video` | Видео | `chats/chat_003/video_files/video_1.mp4` |
| `voice` | Голосовое | `chats/chat_003/voice_messages/voice_1.ogg` |
| `audio` | Аудио | `chats/chat_003/audio_files/audio_1.mp3` |
| `sticker` | Стикер | `chats/chat_003/stickers/sticker.webp` |
| `animation` | GIF/Анимация | `chats/chat_003/animation/anim_1.mp4` |
| `file` | Документ | `chats/chat_003/files/doc_1.pdf` |

---

## 4. Выходные данные

### 4.1 Структура выходной папки

```
Telegram_Export/
├── Index.md                           # Главная страница
├── Contacts/                          # Заметки контактов
│   ├── Иван Петров.md
│   └── Анна Сидорова.md
├── Saved Messages/                    # Сохранённые сообщения
│   ├── 2023-10-15.md
│   ├── photo_123.jpg                  # Медиа в папке заметки
│   └── video_456.mp4
├── Personal Chats/                    # Личные чаты
│   └── Иван Петров/
│       ├── 2023-10-15.md
│       └── photo_789.jpg
├── Groups/                            # Группы
│   └── Работа/
│       ├── 2023-10-15.md
│       └── document.pdf
├── Channels/                          # Каналы
│   └── Новости/
│       ├── 2023-10-15.md
│       └── image.png
└── Other Chats/                       # Остальные чаты
    └── ...
```

### 4.2 Формат Markdown заметки

```markdown
---
chat_type: channel
chat_name: Библиотека программиста
chat_id: 123456789
date: 2023-10-15
message_count: 42
tags:
  - telegram
  - daily-note
---

# 📅 2023-10-15

*Всего сообщений: 42*

==================================================

⏰ **10:30:00** — *Автор*

Текст сообщения с **форматированием**, [ссылками](https://...) и `кодом`.

![photo_1.jpg](photo_1.jpg)

*Реакции:* 👍×9

---

⏰ **11:45:00** — *Другой автор*

Ещё одно сообщение...

> 📤 Переслано от: Original Author

---
```

### 4.3 Форматирование текста

| Telegram Entity | Markdown |
|-----------------|----------|
| `bold` | `**текст**` |
| `italic` | `*текст*` |
| `code` | `` `текст` `` |
| `pre` | ```` ```\nтекст\n``` ```` |
| `underline` | `<u>текст</u>` |
| `strikethrough` | `~~текст~~` |
| `link` / `text_link` | `[текст](href)` |
| `mention` | `[@user](https://t.me/user)` |
| `email` | `[email](mailto:email)` |
| `spoiler` | `> [!spoiler] текст` или `||текст||` |

### 4.4 Frontmatter (YAML)

```yaml
---
chat_type: personal_chat          # Тип чата
chat_name: Иван Петров             # Имя чата
chat_id: 123456789                # ID чата
date: 2023-10-15                  # Дата сообщений
message_count: 42                 # Количество сообщений
tags:
  - telegram
  - daily-note
---
```

---

## 5. Конфигурация

### 5.1 Файл .env

```env
# ===================== ПУТИ =====================

# Путь к JSON файлу экспорта Telegram
TELEGRAM_JSON_FILE=/home/konstantin/Загрузки/Telegram Desktop/DataExport_2026-03-26/result.json

# Корневая папка, где лежат медиафайлы
TELEGRAM_EXPORT_BASE=/home/konstantin/Загрузки/Telegram Desktop/DataExport_2026-03-26

# Папка для сохранения заметок Obsidian
OBSIDIAN_OUTPUT_DIR=/home/konstantin/Документы/ObsidianData/ObsidianData

# Папка для скрипта
SCRIPT_DIR=/home/konstantin/Документы/telegram_obsidian_sync

# Путь к файлу patch.txt
PATCH_FILE=/home/konstantin/Документы/telegram_obsidian_sync/patch.txt

# ===================== ОПЦИИ КОНВЕРТАЦИИ =====================

# Генерировать patch.txt автоматически
GENERATE_PATCH_FILE=true

# Копировать ли медиафайлы
COPY_MEDIA=true

# Копировать ли аватарки
COPY_PROFILE_PICS=true

# Создавать ли индексный файл
CREATE_INDEX=true

# Создавать ли заметки контактов
CREATE_CONTACTS=true

# Добавлять ли frontmatter
CREATE_FRONTMATTER=true

# Преобразовывать ли спойлеры в callout
SPOILER_AS_CALLOUT=true

# Группировать сообщения по дням
GROUP_BY_DAY=true

# Минимальное количество сообщений для файла дня
MIN_MESSAGES_PER_DAY=1

# ===================== AI НАСТРОЙКИ =====================

# Включить AI-интеграцию
AI_ENABLED=false

# AI провайдер: ollama, groq, openai, deepseek, gigachat
AI_PROVIDER=ollama

# Модель для чата
AI_MODEL=llama3.2:1b

# Модель для эмбеддингов
EMBEDDING_MODEL=nomic-embed-text

# URL API
AI_API_URL=http://localhost:11434

# API ключ (для онлайн провайдеров)
AI_API_KEY=
```

### 5.2 Описание параметров

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|--------------|----------|
| `TELEGRAM_JSON_FILE` | string | `result.json` | Путь к result.json |
| `TELEGRAM_EXPORT_BASE` | string | `.` | Папка экспорта Telegram |
| `OBSIDIAN_OUTPUT_DIR` | string | `Telegram_Export` | Папка вывода Obsidian |
| `GENERATE_PATCH_FILE` | bool | `true` | Генерировать patch.txt |
| `COPY_MEDIA` | bool | `true` | Копировать медиафайлы |
| `COPY_PROFILE_PICS` | bool | `true` | Копировать аватарки |
| `CREATE_INDEX` | bool | `true` | Создавать индексный файл |
| `CREATE_CONTACTS` | bool | `true` | Создавать заметки контактов |
| `CREATE_FRONTMATTER` | bool | `true` | Добавлять YAML frontmatter |
| `SPOILER_AS_CALLOUT` | bool | `true` | Спойлеры как callout |
| `GROUP_BY_DAY` | bool | `true` | Группировка по дням |
| `MIN_MESSAGES_PER_DAY` | int | `1` | Мин. сообщений для файла дня |

---

## 6. Спецификация модулей

### 6.1 Класс TelegramToObsidian

**Файл:** `telegram_to_obsidian.py`

```python
class TelegramToObsidian:
    """
    Основной класс конвертера Telegram экспорта в Obsidian заметки
    
    Атрибуты:
        data: Dict - загруженные данные JSON
        stats: Dict - статистика конвертации
        media_cache: Dict - кэш скопированных медиафайлов
        media_index: Dict - индекс медиафайлов из patch.txt
    
    Методы:
        sanitize_filename(name: str) -> str
        generate_patch_file() -> bool
        index_media_from_patch() -> None
        find_media_file(file_path: str) -> Optional[Path]
        copy_media_file(source_path: str, note_folder: Path) -> Optional[str]
        html_to_markdown(html_content: str) -> str
        parse_text_entities(text, entities) -> str
        format_message(msg: Dict, note_folder: Path) -> str
        build_frontmatter(...) -> str
        create_chat_folder(...) -> Path
        process_chat(chat: Dict, index: int, total: int) -> None
        copy_profile_pictures(data: Dict) -> None
        create_contact_notes(data: Dict) -> None
        create_index(data: Dict) -> None
        load_data() -> bool
        run() -> None
    """
```

### 6.2 Метод generate_patch_file

**Назначение:** Генерация индекса медиафайлов через `ls -R`

**Вход:** Нет  
**Выход:** `bool` (успех/ошибка)

**Алгоритм:**
1. Проверить флаг `GENERATE_PATCH_FILE`
2. Выполнить `ls -R EXPORT_BASE`
3. Сохранить вывод в `PATCH_FILE`
4. Вызвать `index_media_from_patch()`
5. Вернуть `True` при успехе

**Код:**
```python
def generate_patch_file(self) -> bool:
    if not GENERATE_PATCH_FILE:
        print("ℹ️  Автоматическая генерация patch.txt отключена")
        if PATCH_FILE.exists():
            self.index_media_from_patch()
        return False
    
    try:
        result = subprocess.run(
            ['ls', '-R', str(EXPORT_BASE)],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8'
        )
        
        with open(PATCH_FILE, 'w', encoding='utf-8') as f:
            f.write(result.stdout)
        
        self.index_media_from_patch()
        self.stats['patch_generated'] = True
        return True
    except Exception as e:
        print(f"❌ Ошибка генерации patch.txt: {e}")
        return False
```

### 6.3 Метод index_media_from_patch

**Назначение:** Парсинг patch.txt и построение индекса медиафайлов

**Вход:** Нет  
**Выход:** Нет (заполняет `self.media_index`)

**Алгоритм:**
1. Открыть `PATCH_FILE`
2. Парсить строки формата `ls -R`
3. Для каждого медиафайла создать 3 ключа:
   - Имя файла
   - Относительный путь от EXPORT_BASE
   - Путь с префиксом `chats/`
4. Сохранить в `self.media_index`

**Код:**
```python
def index_media_from_patch(self):
    media_extensions = {
        '.jpg', '.jpeg', '.png', '.gif', '.webp',
        '.mp4', '.webm', '.tgs', '.tgv',
        '.pdf', '.zip', '.vcard', '.mp3', '.ogg', '.wav'
    }
    current_dir = None
    count = 0
    
    with open(PATCH_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.endswith(':'):
                current_dir = line[:-1]
                continue
            if current_dir:
                if any(line.endswith(ext) for ext in media_extensions):
                    full_path = Path(current_dir) / line
                    file_name = line
                    
                    # Ключ 1: имя файла
                    self.media_index[file_name] = full_path
                    
                    # Ключ 2: относительный путь
                    if str(full_path).startswith(str(EXPORT_BASE)):
                        try:
                            rel_path = full_path.relative_to(EXPORT_BASE)
                            self.media_index[str(rel_path)] = full_path
                        except ValueError:
                            pass
                    
                    # Ключ 3: путь с chats/
                    if 'chats/' in str(full_path):
                        rel_path = str(full_path).split('chats/', 1)[-1]
                        self.media_index[f"chats/{rel_path}"] = full_path
                        self.media_index[rel_path] = full_path
                    
                    count += 1
    
    print(f"✅ Проиндексировано {count} медиафайлов")
```

### 6.4 Метод find_media_file

**Назначение:** Поиск файла медиа по пути из JSON

**Вход:** `file_path: str`  
**Выход:** `Optional[Path]`

**Стратегии поиска:**
1. Поиск по имени файла в индексе
2. Поиск по полному пути в индексе
3. Поиск по частичному совпадению
4. Прямой путь относительно EXPORT_BASE
5. Глубокий поиск через `rglob`

**Код:**
```python
def find_media_file(self, file_path: str) -> Optional[Path]:
    if not file_path or "(File not included" in str(file_path):
        return None
    
    file_name = Path(file_path).name
    
    # Стратегия 1: Поиск по имени
    if file_name in self.media_index:
        source_file = self.media_index[file_name]
        if source_file.exists():
            return source_file
    
    # Стратегия 2: Поиск по полному пути
    if file_path in self.media_index:
        source_file = self.media_index[file_path]
        if source_file.exists():
            return source_file
    
    # Стратегия 3: Частичное совпадение
    for index_name, index_path in self.media_index.items():
        if index_path.exists() and index_path.name == file_name:
            return index_path
    
    # Стратегия 4: Прямой путь
    possible_paths = [
        EXPORT_BASE / file_path,
        EXPORT_BASE / file_path.replace('chats/', ''),
        EXPORT_BASE / 'chats' / file_path.replace('chats/', ''),
    ]
    for path in possible_paths:
        if path.exists():
            return path
    
    # Стратегия 5: Глубокий поиск
    chats_dir = EXPORT_BASE / 'chats'
    if chats_dir.exists():
        for match in chats_dir.rglob(file_name):
            if match.is_file():
                return match
    
    return None
```

### 6.5 Метод copy_media_file

**Назначение:** Копирование медиафайла в папку заметки

**Вход:** 
- `source_path: str` - путь из JSON
- `note_folder: Path` - папка целевой заметки

**Выход:** `Optional[str]` - относительный путь для Markdown

**Алгоритм:**
1. Проверить кэш
2. Найти файл через `find_media_file()`
3. Создать целевую директорию (папка заметки)
4. Скопировать файл с обработкой коллизий имён
5. Вернуть имя файла для Markdown

**Код:**
```python
def copy_media_file(self, source_path: str, note_folder: Path = None) -> Optional[str]:
    if not COPY_MEDIA or not source_path:
        return None
    
    # Проверка кэша
    if source_path in self.media_cache:
        return self.media_cache[source_path]['obsidian']
    
    # Поиск файла
    source_file = self.find_media_file(source_path)
    if not source_file or not source_file.exists():
        print(f"⚠️  Файл не найден: {source_path}")
        return None
    
    # Целевая директория — папка заметки
    target_dir = note_folder if note_folder else OUTPUT_DIR / "Attachments"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    target_file = target_dir / source_file.name
    
    # Обработка коллизий
    if target_file.exists():
        stem = target_file.stem
        suffix = target_file.suffix
        counter = 1
        while target_file.exists():
            target_file = target_dir / f"{stem}_{counter}{suffix}"
            counter += 1
    
    # Копирование
    try:
        shutil.copy2(source_file, target_file)
        self.stats['media_files'] += 1
        
        result_path = source_file.name
        
        self.media_cache[source_path] = {
            'obsidian': result_path,
            'source': str(source_file)
        }
        return result_path
    except Exception as e:
        print(f"⚠️  Ошибка копирования: {e}")
        return None
```

### 6.6 Метод format_message

**Назначение:** Форматирование сообщения в Markdown

**Вход:** 
- `msg: Dict` - сообщение из JSON
- `note_folder: Path` - папка заметки

**Выход:** `str` - Markdown текст

**Алгоритм:**
1. Извлечь время и отправителя
2. Обработать текст через `parse_text_entities()`
3. Определить тип медиа по ключу (`photo`, `video`, etc.)
4. Скопировать медиа через `copy_media_file()`
5. Сформировать Markdown с ссылками на медиа
6. Добавить реакции

**Код:**
```python
def format_message(self, msg: Dict, note_folder: Path = None) -> str:
    content = []
    
    # Время и отправитель
    date = msg.get('date', '')
    if date:
        time_part = date.split(' ')[-1] if ' ' in date else date
        content.append(f"⏰ **{time_part}**")
    
    sender = msg.get('from')
    if sender:
        content.append(f" — *{sender}*")
    content.append("\n\n")
    
    # Текст
    text = msg.get('text', '')
    entities = msg.get('text_entities')
    if text or entities:
        body = self.parse_text_entities(text, entities)
        if body and body.strip():
            content.append(f"{body.strip()}\n\n")
    
    # Медиа — проверка наличия ключей (не media_type!)
    file_path = None
    media_type = None
    
    if 'photo' in msg:
        file_path = msg.get('photo')
        media_type = 'photo'
    elif 'video' in msg:
        file_path = msg.get('video')
        media_type = 'video_file'
    elif 'voice' in msg:
        file_path = msg.get('voice')
        media_type = 'voice_message'
    elif 'audio' in msg:
        file_path = msg.get('audio')
        media_type = 'audio_file'
    elif 'sticker' in msg:
        file_path = msg.get('sticker')
        media_type = 'sticker'
    elif 'animation' in msg:
        file_path = msg.get('animation')
        media_type = 'animation'
    else:
        file_path = msg.get('file')
        media_type = msg.get('media_type')
    
    if file_path and "(File not included" not in str(file_path):
        copied_path = self.copy_media_file(file_path, note_folder)
        if copied_path:
            file_name = msg.get('file_name', Path(file_path).name)
            if media_type in ['photo', 'sticker', 'animation', 'video_message']:
                content.append(f"![{file_name}]({copied_path})\n\n")
            else:
                content.append(f"[{file_name}]({copied_path})\n\n")
    
    # Реакции
    reactions = msg.get('reactions')
    if reactions:
        rx = " ".join([f"{r.get('emoji','')}×{r.get('count',0)}" for r in reactions])
        content.append(f"*Реакции:* {rx}\n\n")
    
    content.append("---\n\n")
    return ''.join(content)
```

---

## 7. AI-интеграция

### 7.1 Поддерживаемые провайдеры

| Провайдер | Модель | URL | Цена |
|-----------|--------|-----|------|
| Ollama | llama3.2:1b | http://localhost:11434 | Бесплатно |
| Groq | llama-3.1-8b | https://api.groq.com | Бесплатно* |
| DeepSeek | deepseek-chat | https://api.deepseek.com | $0.27/1M |
| Qwen | qwen-3.5-72b | https://api.openrouter.ai | $0.50/1M |
| GigaChat | GigaChat-Pro | https://gigachat.sber.ru | ~₽50/1M |

*Groq имеет бесплатный тариф с лимитами

### 7.2 Интерфейс AI клиента

```python
class BaseAIClient:
    """Базовый класс для AI клиентов"""
    
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
    
    def chat(self, prompt: str, context: List[Dict]) -> str:
        """Отправить запрос и получить ответ"""
        pass
    
    def embeddings(self, text: str) -> List[float]:
        """Получить эмбеддинги текста"""
        pass
    
    def is_available(self) -> bool:
        """Проверить доступность API"""
        pass
```

### 7.3 Ollama клиент

```python
class OllamaClient(BaseAIClient):
    """Клиент для локальной модели Ollama"""
    
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"):
        super().__init__("", base_url, model)
    
    def chat(self, prompt: str, context: List[Dict] = None) -> str:
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": context or [{"role": "user", "content": prompt}]
            }
        )
        return response.json()['message']['content']
    
    def embeddings(self, text: str) -> List[float]:
        response = requests.post(
            f"{self.base_url}/api/embeddings",
            json={"model": "nomic-embed-text", "prompt": text}
        )
        return response.json()['embedding']
    
    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except:
            return False
```

---

## 8. Требования к тестированию

### 8.1 Unit тесты

| Тест | Описание | Ожидаемый результат |
|------|----------|---------------------|
| `test_json_parsing` | Парсинг result.json | Успешная загрузка данных |
| `test_media_indexing` | Индексация patch.txt | Индекс заполнен |
| `test_markdown_generation` | Генерация Markdown | Валидный Markdown |
| `test_file_copying` | Копирование файлов | Файлы скопированы |
| `test_frontmatter` | YAML frontmatter | Валидный YAML |
| `test_ollama_connection` | Подключение к Ollama | API доступен |

### 8.2 Integration тесты

| Тест | Описание |
|------|----------|
| `test_full_conversion` | Полный цикл конвертации |
| `test_ai_search` | AI-поиск по заметкам |
| `test_large_export` | Экспорт 10000+ сообщений |

### 8.3 Покрытие тестами

| Компонент | Минимальное покрытие |
|-----------|---------------------|
| Конвертер | 80% |
| AI модуль | 70% |
| CLI | 60% |
| Утилиты | 50% |

---

## 9. Требования к развёртыванию

### 9.1 Системные требования

| Ресурс | Минимальные | Рекомендуемые |
|--------|-------------|---------------|
| OS | Linux/macOS/Windows 10+ | Linux/macOS |
| Python | 3.7+ | 3.10+ |
| RAM | 4 GB (без AI) | 16 GB (с AI) |
| Disk | 10 GB | 50+ GB |
| GPU | Не требуется | NVIDIA 8GB+ (для AI) |

### 9.2 Установка

```bash
# Клонирование
git clone git@github.com:Inna949Festchuk/telegram_obsidian_sync.git
cd telegram_obsidian_sync

# Виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Копирование конфигурации
cp .env.example .env
# Редактирование .env

# Запуск
python telegram_to_obsidian.py
```

### 9.3 Зависимости

**requirements.txt:**
```txt
python-dotenv==1.0.0
requests==2.31.0
```

---

## 10. Обработка ошибок

### 10.1 Типы ошибок

| Ошибка | Причина | Решение |
|--------|---------|---------|
| `FileNotFoundError` | JSON файл не найден | Проверить путь в .env |
| `JSONDecodeError` | Неверный формат JSON | Проверить целостность экспорта |
| `PermissionError` | Нет прав на запись | Проверить права на папку |
| `SubprocessError` | Ошибка ls -R | Проверить путь экспорта |
| `ConnectionError` | AI API недоступен | Проверить подключение |

### 10.2 Логирование

**Уровни логов:**
- `INFO` — нормальная работа
- `WARNING` — предупреждения
- `ERROR` — ошибки

**Формат:**
```
[YYYY-MM-DD HH:MM:SS] LEVEL: message
```

---

## 11. Производительность

### 11.1 Целевые метрики

| Метрика | Значение |
|---------|----------|
| Конвертация 10000 сообщений | < 30 минут |
| Потребление памяти | < 2 GB |
| Индексация 50000 файлов | < 5 минут |
| AI ответ | < 5 секунд |

### 11.2 Оптимизации

1. **Кэширование медиа** — не копировать дубликаты
2. **Группировка по дням** — меньше файлов
3. **Параллельная обработка** — многопоточность для чатов
4. **Инкрементальная конвертация** — только новые сообщения

---

## 12. Критерии приёмки

### 12.1 Функциональные

- [ ] Конвертация JSON в Markdown работает
- [ ] Медиафайлы копируются в папку заметки
- [ ] Frontmatter добавляется к заметкам
- [ ] Группировка по дням работает
- [ ] Индексный файл создаётся
- [ ] Контакты экспортируются
- [ ] AI-интеграция работает (Ollama + 1 онлайн)

### 12.2 Нефункциональные

- [ ] Конвертация 10000 сообщений < 30 минут
- [ ] Потребление памяти < 2 GB
- [ ] Обработка ошибок с понятными сообщениями
- [ ] Логирование всех операций
- [ ] Поддержка UTF-8 (русские символы)

### 12.3 Безопасность

- [ ] .env не коммитится в git
- [ ] API ключи не логируются
- [ ] Проверка путей на инъекции
- [ ] Валидация входных данных

---

## 13. Roadmap

### Версия 1.0 (MVP)
- [ ] Базовая конвертация JSON → Markdown
- [ ] Копирование медиафайлов
- [ ] Группировка по дням
- [ ] Frontmatter
- [ ] CLI интерфейс

### Версия 1.1
- [ ] AI-интеграция (Ollama)
- [ ] Онлайн API клиенты (Groq)
- [ ] Улучшенная обработка ошибок
- [ ] Документация

### Версия 1.2
- [ ] GUI интерфейс
- [ ] REST API
- [ ] Docker поддержка
- [ ] CI/CD pipeline

### Версия 2.0
- [ ] Инкрементальная конвертация
- [ ] Поддержка других мессенджеров
- [ ] Веб-версия приложения
- [ ] Плагины для Obsidian

---

## 14. Контакты и поддержка

| Роль | Контакт |
|------|---------|
| Автор | Konstantin Festchuk |
| Email | festchuk@yandex.ru |
| Telegram | @Dilmah949 |
| GitHub | Inna949Festchuk/telegram_obsidian_sync |

---

## 15. Приложения

### Приложение A: Примеры кода

#### A.1 Минимальный рабочий пример

```python
from telegram_to_obsidian import TelegramToObsidian

converter = TelegramToObsidian()
converter.run()
```

#### A.2 Настройка AI

```python
from ai_integration import AIManager

ai = AIManager({
    'provider': 'ollama',
    'model': 'llama3.2:1b',
    'embedding_model': 'nomic-embed-text',
    'api_url': 'http://localhost:11434'
})

answer = ai.chat("Что я сохранил про Python?", notes_context=notes)
print(answer)
```

### Приложение B: Чек-лист перед релизом

- [ ] Все тесты проходят
- [ ] Документация актуальна
- [ ] .env.example обновлён
- [ ] README.md проверен
- [ ] Версия в setup.py обновлена
- [ ] Changelog обновлён
- [ ] GitHub Release создан

---

**Документ версии:** 1.0  
**Дата создания:** Апрель 2026  
**Статус:** Готов к реализации