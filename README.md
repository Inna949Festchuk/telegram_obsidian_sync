# 📱 Telegram Export to Obsidian Converter

Конвертирует HTML-экспорт Telegram в заметки Obsidian с полной поддержкой медиафайлов, форматирования и группировки по дням.

![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Возможности

- 📝 **Преобразование сообщений** — все сообщения конвертируются в заметки Obsidian
- 🖼️ **Медиафайлы** — фото, видео, стикеры, документы копируются в папку Attachments
- 🔗 **Ссылки и форматирование** — сохраняются все ссылки, жирный текст, курсив, код
- 🎭 **Спойлеры** — преобразуются в callout Obsidian или скрытый текст
- 👥 **Контакты** — создаются отдельные заметки для всех контактов
- 📊 **Dataview поддержка** — расширенный frontmatter для аналитики
- 📑 **Индексный файл** — главная страница со статистикой и примерами запросов
- 🚀 **Группировка по дням** — сообщения группируются по датам для лучшей производительности
- 📂 **Поддержка HTML** — работает с HTML-экспортом Telegram Desktop

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

   ![Выбор тех данных, которые Вы хотите сохранить.](https://baj.media/wp-content/uploads/2024/06/telegram_eksport_dannykh_3.png)
   
   ![Экспорт данных Telegram - выбор типов данных](https://baj.media/wp-content/uploads/2024/06/telegram_eksport_dannykh_5.png)
   
   Рекомендуемые настройки:
   - ✅ **Личные данные** (личные переписки)
   - ✅ **Частные группы**
   - ✅ **Частные каналы**
   - ✅ **Фотографии**
   - ✅ **Видео**
   - ✅ **Голосовые сообщения** (если нужны)
   - ✅ **Стикеры** (если нужны)

4. **Выберите формат и путь сохранения:**
   
   - **Формат:** HTML, JSON, оба (рекомендуется)
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

5. **Выберите формат HTML** и нажмите «Экспортировать»

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

### 🔌 Рекомендуемые плагины

После установки Obsidian рекомендуется включить следующие плагины:

#### Обязательные плагины:

1. **Dataview**
   - **Зачем нужен:** Для аналитики и запросов к вашим данным
   - **Установка:** Settings → Community plugins → Browse → поиск "Dataview" → Install → Enable
   - 🔗 [Dataview Documentation](https://blacksmithgu.github.io/obsidian-dataview/)

2. **Obsidian Attachment Management**
   - **Зачем нужен:** Для удобного управления медиафайлами
   - **Установка:** Settings → Community plugins → Browse → поиск "Attachment Management"

3. **Better Word Count**
   - **Зачем нужен:** Подсчет слов и символов в заметках
   - **Установка:** Settings → Community plugins → Browse → поиск "Better Word Count"

#### Дополнительные плагины:

4. **Calendar**
   - Показывает календарь с днями, когда были созданы заметки
   - Удобная навигация по сообщениям по датам

5. **QuickAdd**
   - Быстрое создание заметок и выполнение скриптов

6. **Templater**
   - Создание шаблонов для новых заметок

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
pip install beautifulsoup4==4.12.3 python-dotenv==1.0.0
```

---

## ⚙️ Настройка конвертера

### Создание файла `.env`

Создайте файл `.env` в папке со скриптом:

```env
# Путь к JSON файлу экспорта Telegram (для метаданных)
TELEGRAM_JSON_FILE=/home/konstantin/Загрузки/Telegram Desktop/DataExport_2026-03-26/result.json

# Корневая папка, где лежат медиафайлы и HTML
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

# Добавлять ли frontmatter (обязательно true для Dataview)
CREATE_FRONTMATTER=true

# Преобразовывать ли спойлеры в callout Obsidian
SPOILER_AS_CALLOUT=true

# Группировать сообщения по дням (рекомендуется для больших экспортов)
GROUP_BY_DAY=true

# Минимальное количество сообщений для создания файла дня
MIN_MESSAGES_PER_DAY=1
```

### Описание настроек

| Параметр | Описание | Значения |
|----------|----------|----------|
| `TELEGRAM_JSON_FILE` | Путь к файлу result.json (для метаданных чатов) | путь к файлу |
| `TELEGRAM_EXPORT_BASE` | Корневая папка экспорта Telegram | путь к папке |
| `OBSIDIAN_OUTPUT_DIR` | Папка для сохранения заметок | путь к папке |
| `COPY_MEDIA` | Копировать ли медиафайлы | true/false |
| `COPY_PROFILE_PICS` | Копировать ли аватарки | true/false |
| `CREATE_INDEX` | Создавать ли индексный файл | true/false |
| `CREATE_CONTACTS` | Создавать ли заметки контактов | true/false |
| `CREATE_FRONTMATTER` | Добавлять ли frontmatter | true/false |
| `SPOILER_AS_CALLOUT` | Спойлеры как callout Obsidian | true/false |
| `GROUP_BY_DAY` | Группировать сообщения по дням | true/false |
| `MIN_MESSAGES_PER_DAY` | Мин. сообщений для файла дня | число |

---

## 🚀 Использование

### Запуск конвертации

```bash
python telegram_to_obsidian.py
```

### Процесс конвертации

1. Скрипт загружает JSON файл экспорта (для метаданных чатов)
2. Сканирует папку `chats/` для поиска HTML файлов сообщений
3. Парсит HTML файлы с помощью BeautifulSoup
4. Копирует медиафайлы из `chats/chat_XXX/photos/`, `stickers/`, `video_files/`
5. Создаёт заметки контактов
6. Формирует индексный файл

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

## 📊 Frontmatter для Dataview

Каждая заметка содержит расширенный frontmatter для работы с плагином Dataview:

```yaml
---
# Основные поля
chat_type: personal_chat          # Тип чата
chat_name: Иван Петров             # Имя чата
chat_id: 123456789                # ID чата
date: 2023-10-15                  # Дата сообщений (при группировке по дням)
message_count: 42                 # Количество сообщений за день

# Теги
tags:
  - telegram
  - personal_chat
  - chat_ivan_petrov
---
```

---

## 🔍 Примеры Dataview запросов

### 1. Последние 20 дней с сообщениями

```dataview
TABLE date AS "Дата", chat_name AS "Чат", message_count AS "Сообщений"
FROM "Telegram_Export"
SORT date DESC
LIMIT 20
```

### 2. Чаты с наибольшим количеством сообщений

```dataview
TABLE sum(message_count) AS "Всего сообщений"
FROM "Telegram_Export"
GROUP BY chat_name
SORT sum(message_count) DESC
LIMIT 10
```

### 3. Сообщения с медиафайлами

```dataview
TABLE date AS "Дата", chat_name AS "Чат"
FROM "Telegram_Export"
WHERE contains(file.name, "Attachments")
SORT date DESC
LIMIT 50
```

### 4. Ежедневная активность (DataviewJS)

```javascript
const messages = dv.pages('"Telegram_Export"')
  .where(p => p.date)
  .groupBy(p => p.date);

let daily = [];
for (let group of messages) {
  daily.push({
    date: group.key,
    count: group.rows.values.reduce((sum, p) => sum + (p.message_count || 0), 0)
  });
}

daily.sort((a, b) => b.date.localeCompare(a.date));
dv.table(
  ["Дата", "Сообщений"],
  daily.slice(0, 30).map(d => [d.date, d.count])
);
```

### 5. Дашборд с общей статистикой (DataviewJS)

```javascript
const allPages = dv.pages('"Telegram_Export"');
const totalDays = allPages.length;
const totalMessages = allPages.values.reduce((sum, p) => sum + (p.message_count || 0), 0);
const chats = allPages.values.map(p => p.chat_name).unique().length;

dv.paragraph(`
## 📊 Общая статистика

- **Всего дней:** ${totalDays}
- **Всего сообщений:** ${totalMessages.toLocaleString()}
- **Всего чатов:** ${chats}
- **Среднее сообщений в день:** ${Math.round(totalMessages/totalDays)}
`);
```

---

## 🎯 Рекомендации по использованию в Obsidian

### 1. Установите необходимые плагины

- **Dataview** — для продвинутой аналитики и запросов
- **Obsidian Attachment Management** — для управления медиафайлами
- **Better Word Count** — для подсчёта слов и символов
- **Calendar** — для навигации по датам

### 2. Создайте дашборд

Создайте новую заметку `Dashboard.md` и добавьте туда свои Dataview запросы для быстрого доступа к статистике.

### 3. Настройте шаблоны

Создайте шаблоны для новых заметок с нужным frontmatter.

### 4. Используйте граф связей

**Obsidian Graph View** покажет связи между сообщениями, контактами и тегами.

### 5. Настройте горячие клавиши

Настройте горячие клавиши для быстрого поиска и навигации.

---

## 🐛 Устранение неполадок

### Проблема: Не копируются медиафайлы

**Решение:**
- Проверьте путь `TELEGRAM_EXPORT_BASE` в `.env`
- Убедитесь, что файлы существуют в папке `chats/chat_XXX/photos/`
- Проверьте права на запись в папку вывода

### Проблема: Не создаются заметки

**Решение:**
- Проверьте права на запись в папку вывода
- Убедитесь, что HTML файлы существуют в папке экспорта
- Проверьте свободное место на диске

### Проблема: Dataview не видит поля

**Решение:**
- Убедитесь, что `CREATE_FRONTMATTER=true` в `.env`
- Перезапустите скрипт для обновления frontmatter
- Проверьте, что заметки находятся в правильной папке

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
| beautifulsoup4 | 4.12.3 | Парсинг HTML |
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
- [Obsidian Plugins](https://obsidian.md/plugins) — сообщество плагинов

### Плагины Obsidian
- [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) — документация
- [Templater](https://silentvoid13.github.io/Templater/) — шаблоны
- [QuickAdd](https://github.com/chhoumann/quickadd) — быстрое создание заметок

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

