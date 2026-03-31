# 📱 Telegram to Obsidian Converter

Конвертирует экспорт данных Telegram в заметки Obsidian с полной поддержкой медиафайлов, форматирования и группировки по дням.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Возможности

- 📝 **Преобразование сообщений** — все сообщения конвертируются в заметки Markdown
- 🖼️ **Медиафайлы** — фото, видео, стикеры, документы копируются в папку Attachments
- 🔗 **Ссылки и форматирование** — сохраняются все ссылки, жирный текст, курсив, код
- 🎭 **Спойлеры** — преобразуются в callout блоки или скрытый текст
- 👥 **Контакты** — создаются отдельные заметки для всех контактов
- 📑 **Индексный файл** — главная страница со статистикой экспорта
- 🚀 **Группировка по дням** — сообщения группируются по датам для лучшей организации
- 📂 **Поддержка JSON** — работает с JSON-экспортом Telegram Desktop

---

## 📥 Шаг 1: Экспорт данных из Telegram

### 📋 Подготовка экспорта

Для работы конвертера необходимо сначала экспортировать данные из Telegram. **Важно:** экспорт доступен **только в десктопной версии** Telegram!

#### Вариант 1: Полный экспорт всех чатов

1. **Откройте Telegram Desktop** на вашем компьютере

2. **Перейдите в настройки экспорта:**
   
   ```
   Настройки → Продвинутые настройки → Экспорт данных из Telegram
   ```
   
   *(Прокрутите настройки до самого конца)*

3. **Выберите данные для экспорта:**
   
   Рекомендуемые настройки:
   - ✅ **Личные данные** (личные переписки)
   - ✅ **Частные группы**
   - ✅ **Частные каналы**
   - ✅ **Фотографии**
   - ✅ **Видео**
   - ✅ **Голосовые сообщения** (если нужны)
   - ✅ **Стикеры** (если нужны)

4. **Выберите формат и путь сохранения:**
   
   - **Формат:** JSON (обязательно), HTML (опционально)
   - **Размер медиа:** выберите подходящий (для полного экспорта — максимальный)
   - **Путь сохранения:** укажите папку на компьютере

5. **Нажмите «Экспортировать»** и дождитесь завершения процесса

#### Вариант 2: Экспорт конкретного чата

Если нужно экспортировать только определенный чат или канал:

1. **Откройте нужный чат/канал** в Telegram Desktop

2. **Нажмите на меню** (три точки в правом верхнем углу)

3. **Выберите «Экспорт истории чата»**

4. **Отметьте нужные данные:**
   - Фотографии
   - Видео
   - Голосовые сообщения
   - Видео сообщения
   - Стикеры
   - И т.д.

5. **Выберите формат JSON** и нажмите «Экспортировать»

### 📁 Структура экспорта

После экспорта вы получите папку со следующей структурой:

```
DataExport_YYYY-MM-DD/
├── result.json              # Файл с метаданными (обязателен!)
├── chats/
│   ├── chat_001/
│   │   ├── messages.html
│   │   ├── messages2.html
│   │   └── photos/
│   └── chat_002/
│       └── ...
├── profile_pictures/
└── ...
```

**Важно:** Убедитесь, что в экспорте присутствует файл `result.json` — он необходим для работы конвертера!

---

## 📥 Шаг 2: Установка Obsidian

### Скачивание и установка

1. **Перейдите на официальный сайт:**
   
   🔗 [**Скачать Obsidian**](https://obsidian.md/download)

2. **Выберите вашу операционную систему:**
   - Windows (.exe установщик)
   - macOS (.dmg образ)
   - Linux (AppImage, Snap, Flatpak)

3. **Установите приложение** следуя инструкциям установщика

4. **Запустите Obsidian** и создайте новое хранилище (vault):
   - Нажмите «Create new vault»
   - Укажите имя и расположение папки
   - Нажмите «Create»

---

## 🔧 Шаг 3: Установка конвертера

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/telegram-to-obsidian.git
cd telegram-to-obsidian
```

### 2. Создание виртуального окружения (рекомендуется)

**Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

Или вручную:
```bash
pip install python-dotenv==1.0.0
```

---

## ⚙️ Настройка конвертера

### Создание файла `.env`

Создайте файл `.env` в папке со скриптом:

```env
# Путь к JSON файлу экспорта Telegram
TELEGRAM_JSON_FILE=/home/konstantin/Загрузки/Telegram Desktop/DataExport_2026-03-26/result.json

# Корневая папка, где лежат медиафайлы
TELEGRAM_EXPORT_BASE=/home/konstantin/Загрузки/Telegram Desktop/DataExport_2026-03-26

# Папка для сохранения заметок Obsidian
OBSIDIAN_OUTPUT_DIR=/home/konstantin/Документы/ObsidianData/ObsidianData

# Копировать ли медиафайлы
COPY_MEDIA=true

# Копировать ли аватарки
COPY_PROFILE_PICS=true

# Создавать ли индексный файл
CREATE_INDEX=true

# Создавать ли заметки контактов
CREATE_CONTACTS=true

# Добавлять ли frontmatter (метаданные YAML)
CREATE_FRONTMATTER=true

# Преобразовывать ли спойлеры в callout блоки
SPOILER_AS_CALLOUT=true

# Группировать сообщения по дням (рекомендуется для больших экспортов)
GROUP_BY_DAY=true

# Минимальное количество сообщений для создания файла дня
MIN_MESSAGES_PER_DAY=1
```

### Описание настроек

| Параметр | Описание | Значения |
|----------|----------|----------|
| `TELEGRAM_JSON_FILE` | Путь к файлу result.json | путь к файлу |
| `TELEGRAM_EXPORT_BASE` | Корневая папка экспорта Telegram | путь к папке |
| `OBSIDIAN_OUTPUT_DIR` | Папка для сохранения заметок | путь к папке |
| `COPY_MEDIA` | Копировать ли медиафайлы | true/false |
| `COPY_PROFILE_PICS` | Копировать ли аватарки | true/false |
| `CREATE_INDEX` | Создавать ли индексный файл | true/false |
| `CREATE_CONTACTS` | Создавать ли заметки контактов | true/false |
| `CREATE_FRONTMATTER` | Добавлять ли metаданные YAML | true/false |
| `SPOILER_AS_CALLOUT` | Спойлеры как callout блоки | true/false |
| `GROUP_BY_DAY` | Группировать сообщения по дням | true/false |
| `MIN_MESSAGES_PER_DAY` | Мин. сообщений для файла дня | число |

---

## 🚀 Использование

### Запуск конвертации

```bash
python telegram_to_obsidian.py
```

### Процесс конвертации

1. Скрипт загружает JSON файл экспорта
2. Генерирует файл `patch.txt` для индексации медиафайлов
3. Копирует медиафайлы из `chats/chat_XXX/photos/`, `stickers/`, `video_files/`
4. Создаёт заметки контактов
5. Формирует индексный файл

### 📁 Структура выходных данных

```
Telegram_Export/
├── Index.md                           # Главная страница
├── Attachments/                       # Все медиафайлы
│   ├── photo_123.jpg
│   ├── video_456.mp4
│   └── document_789.pdf
├── Profile/                           # Аватарки
│   └── avatar.jpg
├── Contacts/                          # Заметки контактов
│   ├── Иван Петров.md
│   └── Анна Сидорова.md
├── Saved Messages/                    # Сохранённые сообщения
│   ├── 2023-10-15.md                  # Все сообщения за день
│   └── ...
├── Personal Chats/                    # Личные чаты
│   └── Иван Петров/
│       ├── 2023-10-15.md              # Все сообщения за день
│       └── ...
├── Groups/                            # Группы
│   └── Работа/
│       ├── 2023-10-15.md
│       └── ...
├── Channels/                          # Каналы
│   └── Новости/
│       ├── 2023-10-15.md
│       └── ...
└── Other Chats/                       # Остальные чаты
    └── ...
```

---

## 📊 Frontmatter (метаданные YAML)

Каждая заметка содержит метаданные для удобной организации:

```yaml
---
chat_type: personal_chat          # Тип чата
chat_name: Иван Петров             # Имя чата
chat_id: 123456789                # ID чата
date: 2023-10-15                  # Дата сообщений
message_count: 42                 # Количество сообщений
tags:
  - telegram
  - personal_chat
---
```

---

## 🎯 Рекомендации по использованию в Obsidian

### 1. Откройте папку экспорта в Obsidian

- Запустите Obsidian
- Выберите «Open folder as vault»
- Укажите папку `Telegram_Export` или добавьте её в существующее хранилище

### 2. Используйте поиск

**Obsidian Search** позволяет быстро находить сообщения по тексту, датам и контактам.

### 3. Используйте граф связей

**Obsidian Graph View** покажет связи между сообщениями, контактами и тегами.

### 4. Настройте горячие клавиши

Настройте горячие клавиши для быстрого поиска и навигации.

---

## 🐛 Устранение неполадок

### Проблема: Не копируются медиафайлы

**Решение:**
- Проверьте путь `TELEGRAM_EXPORT_BASE` в `.env`
- Убедитесь, что файлы существуют в папке `chats/chat_XXX/photos/`
- Проверьте права на запись в папку вывода
- Удалите файл `patch.txt` и запустите скрипт заново для переиндексации

### Проблема: Не создаются заметки

**Решение:**
- Проверьте права на запись в папку вывода
- Убедитесь, что JSON файл существует в папке экспорта
- Проверьте свободное место на диске

### Проблема: Медленная работа

**Решение:**
- Включите `GROUP_BY_DAY=true` для группировки по дням
- Увеличьте `MIN_MESSAGES_PER_DAY` для уменьшения количества файлов
- Отключите копирование медиа для ускорения

### Проблема: Ошибка при загрузке JSON

**Решение:**
- Проверьте путь к JSON файлу
- Убедитесь, что файл `result.json` существует в папке экспорта
- Проверьте кодировку файла (должна быть UTF-8)

---

## 📦 Зависимости

| Пакет | Версия | Назначение |
|-------|--------|------------|
| python-dotenv | 1.0.0 | Загрузка переменных окружения |

---

## 📝 Полезные ссылки

### Telegram
- [Telegram Desktop](https://desktop.telegram.org/) — скачать десктопную версию
- [Как экспортировать данные из Telegram](https://telegram.org/blog/export)

### Obsidian
- [Obsidian.md](https://obsidian.md/) — официальный сайт
- [Obsidian Download](https://obsidian.md/download) — скачать Obsidian
- [Obsidian Help](https://help.obsidian.md/) — документация

---

## 🤝 Вклад в проект

Приветствуются pull requests и issues!

### Как помочь:

1. Форкните репозиторий
2. Создайте ветку для новой функциональности
3. Внесите изменения
4. Отправьте pull request

### Что можно улучшить:

- Добавить поддержку голосовых сообщений
- Улучшить обработку стикеров
- Добавить экспорт в другие форматы
- Оптимизировать производительность

---

## 📄 Лицензия

MIT License

Copyright (c) 2024 Telegram to Obsidian Converter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## 📞 Контакты

**Автор:** Konstantin Festchuk  
**Email:** festchuk@yandex.ru  
**Telegram:** [@Dilmah949](https://t.me/@Dilmah949)

---

## ⭐ Поддержка проекта

Если вам понравился проект, поставьте звезду на GitHub! Это помогает другим пользователям найти инструмент.

**Сделано с ❤️ для сообщества Obsidian и Telegram**

### **Направление дальнейших исследований:**

привет друг! скажи мне, если я запущу CLI из папки с моими заметками .md obsidian ты сможешь использовать их как базу знаний?


Thinking
Привет! Да, я могу работать с твоими заметками Obsidian (.md файлами) как с базой знаний.

У тебя есть несколько вариантов:

Прямой доступ к файлам — я могу читать .md файлы из твоей папки Obsidian через инструменты read_file, glob, grep_search. Это работает для текущей директории и подпапок.

Если папка Obsidian в другом месте — ты можешь:

Скопировать/переместить заметки в текущую папку
Или указать мне путь к папке (если она доступна из текущей сессии)
Использовать агент для поиска — для сложных запросов по всей базе заметок я могу запустить агента с инструментом Explore, который быстро найдёт нужную информацию по паттернам или ключевым словам.

Ограничения:

Я не могу автоматически индексировать или создавать постоянную базу знаний — каждый запрос обрабатывается заново
Для больших баз (1000+ файлов) поиск может занять время
Хочешь попробовать? Укажи путь к папке с заметками или скажи, какую информацию нужно найти.