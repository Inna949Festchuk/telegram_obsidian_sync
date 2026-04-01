#!/usr/bin/env python3
"""
Telegram Export to Obsidian Converter
Конвертирует экспорт Telegram в заметки Obsidian с полной поддержкой медиафайлов.
Автоматически генерирует patch.txt для индексации медиафайлов.
Медиафайлы копируются в папку заметки.
"""
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import html

# Загрузка переменных окружения из .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Библиотека python-dotenv не установлена.")
    print("    Установите её: pip install python-dotenv")
    print("    Продолжаем с настройками по умолчанию...")

# ===================== НАСТРОЙКИ ИЗ .env =====================
JSON_FILE = os.getenv('TELEGRAM_JSON_FILE', 'result.json')
EXPORT_BASE = Path(os.getenv('TELEGRAM_EXPORT_BASE', '.'))
OUTPUT_DIR = Path(os.getenv('OBSIDIAN_OUTPUT_DIR', 'Telegram_Export'))
SCRIPT_DIR = Path(os.getenv('SCRIPT_DIR', '.'))
PATCH_FILE = Path(os.getenv('PATCH_FILE', 'patch.txt'))
GENERATE_PATCH_FILE = os.getenv('GENERATE_PATCH_FILE', 'true').lower() == 'true'
COPY_MEDIA = os.getenv('COPY_MEDIA', 'true').lower() == 'true'
COPY_PROFILE_PICS = os.getenv('COPY_PROFILE_PICS', 'true').lower() == 'true'
CREATE_INDEX = os.getenv('CREATE_INDEX', 'true').lower() == 'true'
CREATE_CONTACTS = os.getenv('CREATE_CONTACTS', 'true').lower() == 'true'
CREATE_FRONTMATTER = os.getenv('CREATE_FRONTMATTER', 'true').lower() == 'true'
SPOILER_AS_CALLOUT = os.getenv('SPOILER_AS_CALLOUT', 'true').lower() == 'true'
GROUP_BY_DAY = os.getenv('GROUP_BY_DAY', 'true').lower() == 'true'
MIN_MESSAGES_PER_DAY = int(os.getenv('MIN_MESSAGES_PER_DAY', '1'))
# =============================================================

# Создаем выходную директорию
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
SCRIPT_DIR.mkdir(parents=True, exist_ok=True)

# Регулярное выражение для недопустимых символов в именах файлов
INVALID_FILENAME_CHARS = re.compile(r'[\\/*?:"<>|]')


class TelegramToObsidian:
    """Основной класс конвертера Telegram экспорта в Obsidian заметки"""
    
    def __init__(self):
        self.data = None
        self.stats = {
            'chats': 0,
            'messages': 0,
            'media_files': 0,
            'contacts': 0,
            'patch_generated': False
        }
        self.media_cache = {}
        self.media_index = {}  # Индекс медиафайлов из patch.txt
    
    def sanitize_filename(self, name: str) -> str:
        """Очищает имя файла от недопустимых символов"""
        if not name:
            return "unnamed"
        cleaned = INVALID_FILENAME_CHARS.sub('_', str(name))
        cleaned = re.sub(r'_+', '_', cleaned)
        cleaned = cleaned.strip('_ ')
        return cleaned if cleaned else "unnamed"
    
    def generate_patch_file(self) -> bool:
        """
        🆕 Генерирует patch.txt с помощью ls -R
        """
        if not GENERATE_PATCH_FILE:
            print("ℹ️  Автоматическая генерация patch.txt отключена")
            # Даже если генерация отключена, пробуем проиндексировать существующий файл
            if PATCH_FILE.exists():
                self.index_media_from_patch()
            return False
        
        print("\n📋 Генерация patch.txt...")
        print(f"   📁 Источник: {EXPORT_BASE}")
        print(f"   📄 Назначение: {PATCH_FILE}")
        
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
            print(f"   ✅ patch.txt создан: {PATCH_FILE}")
            print(f"   📊 Проиндексировано файлов: {len(self.media_index)}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Ошибка выполнения ls -R: {e}")
            print(f"   stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"   ❌ Ошибка генерации patch.txt: {e}")
            return False
    
    def index_media_from_patch(self):
        """
        🆕 Парсит patch.txt и строит индекс доступных медиафайлов
        Создаёт несколько ключей для каждого файла для надёжного поиска
        """
        if not PATCH_FILE.exists():
            print("⚠️  Файл patch.txt не найден, продолжаем без индексации")
            return
        
        print("\n📂 Индексация медиафайлов из patch.txt...")
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
                if not line:
                    continue
                if line.endswith(':'):
                    current_dir = line[:-1]
                    continue
                if current_dir:
                    if any(line.endswith(ext) for ext in media_extensions):
                        full_path = Path(current_dir) / line
                        file_name = line
                        
                        # Ключ 1: только имя файла (самый важный!)
                        self.media_index[file_name] = full_path
                        
                        # Ключ 2: относительный путь от EXPORT_BASE
                        if str(full_path).startswith(str(EXPORT_BASE)):
                            try:
                                rel_path = full_path.relative_to(EXPORT_BASE)
                                self.media_index[str(rel_path)] = full_path
                            except ValueError:
                                pass
                        
                        # Ключ 3: путь с префиксом chats/ (для совместимости с JSON)
                        if 'chats/' in str(full_path):
                            rel_path = str(full_path).split('chats/', 1)[-1]
                            self.media_index[f"chats/{rel_path}"] = full_path
                            # Также без префикса chats/
                            self.media_index[rel_path] = full_path
                        
                        count += 1
        
        print(f"   ✅ Проиндексировано {count} медиафайлов")
        print(f"   📊 Всего ключей в индексе: {len(self.media_index)}")
    
    def find_media_file(self, file_path: str) -> Optional[Path]:
        """
        🆕 Ищет файл медиа используя индекс из patch.txt
        Пробует несколько стратегий поиска для максимальной надёжности
        """
        if not file_path or "(File not included" in str(file_path):
            return None
        
        file_name = Path(file_path).name
        
        # Стратегия 1: Прямой поиск по имени файла в индексе
        if file_name in self.media_index:
            source_file = self.media_index[file_name]
            if source_file.exists():
                return source_file
        
        # Стратегия 2: Поиск по полному пути из JSON
        if file_path in self.media_index:
            source_file = self.media_index[file_path]
            if source_file.exists():
                return source_file
        
        # Стратегия 3: Поиск по частичному совпадению пути
        for index_name, index_path in self.media_index.items():
            if index_path.exists():
                # Совпадение по имени файла
                if index_path.name == file_name:
                    return index_path
                # Совпадение по концу пути
                if str(index_path).endswith(file_path):
                    return index_path
                # Совпадение по имени без расширения
                if index_path.stem == Path(file_path).stem:
                    return index_path
        
        # Стратегия 4: Пробуем прямой путь относительно EXPORT_BASE
        possible_paths = [
            EXPORT_BASE / file_path,
            EXPORT_BASE / file_path.replace('chats/', ''),
            EXPORT_BASE / 'chats' / file_path.replace('chats/', ''),
        ]
        for path in possible_paths:
            if path.exists():
                return path
        
        # Стратегия 5: Глубокий поиск в подпапках chats/
        chats_dir = EXPORT_BASE / 'chats'
        if chats_dir.exists():
            for match in chats_dir.rglob(file_name):
                if match.is_file():
                    return match
        
        # Стратегия 6: Поиск в profile_pictures
        profile_dir = EXPORT_BASE / 'profile_pictures'
        if profile_dir.exists():
            for match in profile_dir.rglob(file_name):
                if match.is_file():
                    return match
        
        return None
    
    def copy_media_file(self, source_path: str, target_subdir: str = "Attachments",
                        note_folder: Path = None) -> Optional[str]:
        """
        🆕 Копирует файл медиа в папку заметки
        Возвращает только имя файла (так как медиа в той же папке что и заметка)
        """
        if not COPY_MEDIA or not source_path:
            return None
        
        # Проверка кэша
        if source_path in self.media_cache:
            cached = self.media_cache[source_path]
            return cached['obsidian']
        
        # 🆕 Ищем файл используя индекс из patch.txt
        source_file = self.find_media_file(source_path)
        if not source_file or not source_file.exists():
            print(f"      ⚠️  Файл не найден: {source_path}")
            return None
        
        # 🆕 Целевая директория — папка заметки
        if note_folder:
            target_dir = note_folder
        else:
            target_dir = OUTPUT_DIR / target_subdir
        
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Формируем имя целевого файла
        target_file = target_dir / source_file.name
        
        # Если файл уже существует, добавляем счетчик
        if target_file.exists():
            stem = target_file.stem
            suffix = target_file.suffix
            counter = 1
            while target_file.exists():
                target_file = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1
        
        # Копируем файл
        try:
            shutil.copy2(source_file, target_file)
            self.stats['media_files'] += 1
            
            # 🆕 Возвращаем только имя файла (так как медиа в той же папке)
            result_path = source_file.name
            
            # Сохраняем в кэш
            self.media_cache[source_path] = {
                'obsidian': result_path,
                'source': str(source_file)
            }
            print(f"      ✅ Скопировано: {source_file.name} → {target_dir.name}/{result_path}")
            return result_path
        except Exception as e:
            print(f"      ⚠️  Ошибка копирования {source_file.name}: {e}")
            return None
    
    def html_to_markdown(self, html_content: str) -> str:
        """Преобразует HTML в Markdown"""
        if not html_content:
            return ""
        
        html_content = html.unescape(html_content)
        
        # Спойлеры
        if SPOILER_AS_CALLOUT:
            spoiler_pattern = r'<span[^>]*class="[^"]*spoiler[^"]*"[^>]*>(.*?)</span>'
            html_content = re.sub(
                spoiler_pattern,
                lambda m: f"\n> [!spoiler] {self.html_to_markdown(m.group(1))}\n",
                html_content,
                flags=re.DOTALL | re.IGNORECASE
            )
        
        # Ссылки
        link_pattern = r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"[^>]*>(.*?)</a>'
        html_content = re.sub(
            link_pattern,
            lambda m: self._process_link(m.group(1), m.group(2)),
            html_content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Форматирование
        formatting_rules = [
            (r'<strong>(.*?)</strong>', r'**\1**'),
            (r'<b>(.*?)</b>', r'**\1**'),
            (r'<em>(.*?)</em>', r'*\1*'),
            (r'<i>(.*?)</i>', r'*\1*'),
            (r'<code>(.*?)</code>', r'`\1`'),
            (r'<pre>(.*?)</pre>', r'```\n\1\n```'),
            (r'<u>(.*?)</u>', r'<u>\1</u>'),
            (r'<s>(.*?)</s>', r'~~\1~~'),
            (r'<strike>(.*?)</strike>', r'~~\1~~'),
            (r'<del>(.*?)</del>', r'~~\1~~'),
        ]
        
        for pattern, replacement in formatting_rules:
            html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL | re.IGNORECASE)
        
        html_content = re.sub(r'<br\s*/?>', '\n', html_content, flags=re.IGNORECASE)
        html_content = re.sub(r'<p>(.*?)</p>', r'\1\n', html_content, flags=re.DOTALL | re.IGNORECASE)
        html_content = re.sub(r'<[^>]+>', '', html_content)
        html_content = re.sub(r'\n{3,}', '\n\n', html_content)
        
        return html_content.strip()
    
    def _process_link(self, href: str, text: str) -> str:
        """Обрабатывает HTML ссылку"""
        text = self.html_to_markdown(text) if '<' in text else text
        if not href or href == '#':
            return text
        return f"[{text}]({href})"
    
    def parse_text_entities(self, text: Union[str, List], entities: Optional[List[Dict]] = None) -> str:
        """Преобразует текст с форматированием в markdown"""
        if isinstance(text, str) and ('<' in text or '&' in text):
            return self.html_to_markdown(text)
        
        if entities is not None and isinstance(entities, list) and isinstance(text, str):
            return self._process_entities(text, entities)
        
        if isinstance(text, list):
            return self._process_text_list(text)
        
        return str(text) if text else ""
    
    def _process_entities(self, text: str, entities: List[Dict]) -> str:
        """Обрабатывает текст с сущностями Telegram"""
        if not text:
            return ""
        
        result = []
        last_pos = 0
        
        for entity in sorted(entities, key=lambda e: e.get('offset', 0)):
            offset = entity.get('offset', 0)
            length = entity.get('length', 0)
            entity_type = entity.get('type', '')
            
            if offset > last_pos:
                result.append(str(text[last_pos:offset]))
            
            entity_text = text[offset:offset + length] if offset + length <= len(text) else ""
            processed = self._process_single_entity(entity_text, entity_type, entity)
            result.append(str(processed))
            last_pos = offset + length
        
        if last_pos < len(text):
            result.append(str(text[last_pos:]))
        
        # Фильтруем только строки
        result = [str(r) for r in result if r is not None]
        return ''.join(result)
    
    def _process_single_entity(self, text: str, entity_type: str, entity: Dict) -> str:
        """Обрабатывает одну сущность"""
        text = str(text) if text is not None else ""
        
        handlers = {
            'bold': lambda t: f"**{t}**",
            'italic': lambda t: f"*{t}*",
            'code': lambda t: f"`{t}`",
            'pre': lambda t: f"```\n{t}\n```",
            'underline': lambda t: f"<u>{t}</u>",
            'strikethrough': lambda t: f"~~{t}~~",
        }
        
        if entity_type in handlers:
            return handlers[entity_type](text)
        elif entity_type in ['link', 'text_link']:
            href = entity.get('href', text)
            return f"[{text}]({href})"
        elif entity_type == 'mention':
            username = text[1:] if text.startswith('@') else text
            return f"[{text}](https://t.me/{username})"
        elif entity_type == 'email':
            return f"[{text}](mailto:{text})"
        elif entity_type == 'url':
            return f"[{text}]({text})"
        elif entity_type == 'spoiler':
            if SPOILER_AS_CALLOUT:
                return f"\n> [!spoiler] {text}\n"
            return f"||{text}||"
        
        return text
    
    def _process_text_list(self, text_list: List) -> str:
        """Обрабатывает текст в виде списка"""
        if not text_list:
            return ""
        
        result = []
        for item in text_list:
            try:
                if isinstance(item, str):
                    result.append(item)
                elif isinstance(item, dict):
                    chunk = item.get('text', '')
                    entity_type = item.get('type', '')
                    
                    if entity_type == 'bold':
                        result.append(f"**{chunk}**")
                    elif entity_type == 'italic':
                        result.append(f"*{chunk}*")
                    elif entity_type == 'code':
                        result.append(f"`{chunk}`")
                    elif entity_type == 'pre':
                        result.append(f"```\n{chunk}\n```")
                    elif entity_type in ['link', 'text_link']:
                        href = item.get('href', chunk)
                        result.append(f"[{chunk}]({href})")
                    elif entity_type == 'mention':
                        username = chunk[1:] if str(chunk).startswith('@') else chunk
                        result.append(f"[{chunk}](https://t.me/{username})")
                    elif entity_type == 'email':
                        result.append(f"[{chunk}](mailto:{chunk})")
                    elif entity_type == 'url':
                        result.append(f"[{chunk}]({chunk})")
                    elif entity_type == 'underline':
                        result.append(f"<u>{chunk}</u>")
                    elif entity_type == 'strikethrough':
                        result.append(f"~~{chunk}~~")
                    elif entity_type == 'spoiler':
                        if SPOILER_AS_CALLOUT:
                            result.append(f"\n> [!spoiler] {chunk}\n")
                        else:
                            result.append(f"||{chunk}||")
                    else:
                        result.append(str(chunk) if chunk else "")
                elif isinstance(item, list):
                    result.append(self._process_text_list(item))
                else:
                    result.append(str(item))
            except Exception:
                result.append(str(item))
        
        # Фильтруем только строки
        result = [str(r) for r in result if r is not None]
        return ''.join(result)
    
    def format_message(self, msg: Dict, note_folder: Path = None) -> str:
        """
        🆕 Форматирует сообщение в Markdown
        Ключевое исправление: проверяем наличие ключей (photo, video, etc.), а не media_type
        """
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
        
        # Переслано
        if 'forwarded_from' in msg:
            content.append(f"> 📤 Переслано от: {msg['forwarded_from']}\n\n")
        
        # Текст сообщения
        text = msg.get('text', '')
        entities = msg.get('text_entities')
        
        if text or entities:
            try:
                body = self.parse_text_entities(text, entities)
                if body and body.strip():
                    content.append(f"{body.strip()}\n\n")
            except Exception as e:
                if isinstance(text, str):
                    content.append(f"{text}\n\n")
                elif isinstance(text, list):
                    plain = ' '.join(str(t) for t in text if isinstance(t, str))
                    if plain:
                        content.append(f"{plain}\n\n")
        
        # 🆕 Медиафайлы — проверяем НАЛИЧИЕ КЛЮЧЕЙ (не media_type!)
        # В JSON Telegram нет поля media_type для большинства сообщений
        # Наличие ключа photo/video/voice и т.д. определяет тип медиа
        file_path = None
        media_type = None
        
        # Определяем тип медиа по наличию ключей в JSON
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
            # Резервный вариант: проверяем media_type и file
            file_path = msg.get('file')
            media_type = msg.get('media_type')
        
        if file_path and "(File not included" not in str(file_path):
            # 🆕 Передаём note_folder чтобы медиа копировалось в папку заметки
            copied_path = self.copy_media_file(file_path, "Attachments", note_folder)
            
            if copied_path:
                file_name = msg.get('file_name', Path(file_path).name)
                
                # 🆕 Ссылка только на имя файла (медиа в той же папке)
                if media_type in ['photo', 'sticker', 'animation', 'video_message']:
                    content.append(f"![{file_name}]({copied_path})\n\n")
                elif media_type == 'video_file':
                    content.append(f"🎬 [{file_name}]({copied_path})\n\n")
                elif media_type == 'audio_file':
                    content.append(f"🎵 [{file_name}]({copied_path})\n\n")
                else:
                    content.append(f"📎 [{file_name}]({copied_path})\n\n")
            else:
                content.append(f"📎 *Медиа не найдено: {file_path}*\n\n")
        elif media_type:
            content.append(f"📎 *Тип: {media_type}*\n\n")
        
        # Реакции
        reactions = msg.get('reactions')
        if reactions:
            rx = " ".join([f"{r.get('emoji','')}×{r.get('count',0)}" for r in reactions])
            content.append(f"*Реакции:* {rx}\n\n")
        
        content.append("---\n\n")
        return ''.join(content)
    
    def build_frontmatter(self, chat_type: str, chat_name: str, chat_id: int,
                          day_date: str, message_count: int) -> str:
        """Создает YAML frontmatter"""
        if not CREATE_FRONTMATTER:
            return ""
        
        fm = "---\n"
        fm += f"chat_type: {chat_type}\n"
        fm += f"chat_name: {chat_name}\n"
        fm += f"chat_id: {chat_id}\n"
        fm += f"date: {day_date}\n"
        fm += f"message_count: {message_count}\n"
        fm += "tags: [telegram, daily-note]\n"
        fm += "---\n"
        return fm
    
    def create_chat_folder(self, chat_type: str, chat_id: int, chat_name: str = None) -> Path:
        """Создает папку для чата"""
        if not chat_name:
            chat_name = f"Chat_{chat_id}"
        
        safe_name = self.sanitize_filename(chat_name)
        
        folders = {
            'saved_messages': "Saved Messages",
            'personal_chat': f"Personal Chats/{safe_name}",
            'group': f"Groups/{safe_name}",
            'supergroup': f"Groups/{safe_name}",
            'private_supergroup': f"Groups/{safe_name}",
            'public_supergroup': f"Groups/{safe_name}",
            'channel': f"Channels/{safe_name}",
            'public_channel': f"Channels/{safe_name}",
            'private_channel': f"Channels/{safe_name}",
        }
        
        folder_path = folders.get(chat_type, f"Other Chats/{safe_name}")
        folder = OUTPUT_DIR / folder_path
        folder.mkdir(parents=True, exist_ok=True)
        return folder
    
    def process_chat(self, chat: Dict, index: int, total: int):
        """Обрабатывает чат с группировкой по дням"""
        chat_id = chat.get('id', 0)
        chat_type = chat.get('type', 'unknown')
        chat_name = chat.get('name', f"Chat_{chat_id}")
        
        folder = self.create_chat_folder(chat_type, chat_id, chat_name)
        messages = chat.get('messages', [])
        
        print(f"  [{index}/{total}] {chat_type}: {chat_name} ({len(messages)} сообщений)")
        
        if not messages:
            print(f"      ⚠️  Пропущено: {chat_name} (0 сообщений)")
            return
        
        if GROUP_BY_DAY:
            # Группировка по дням
            messages_by_date = {}
            for msg in messages:
                date_str = msg.get('date', '')
                day_key = date_str.split(' ')[0] if ' ' in date_str else (date_str[:10] if date_str else "unknown")
                messages_by_date.setdefault(day_key, []).append(msg)
            
            sorted_dates = sorted(messages_by_date.keys())
            print(f"      📅 Найдено дней: {len(sorted_dates)}")
            
            for day_idx, day_date in enumerate(sorted_dates):
                day_messages = messages_by_date[day_date]
                
                if len(day_messages) < MIN_MESSAGES_PER_DAY:
                    continue
                
                safe_date = day_date.replace(':', '-').replace(' ', '_')
                filename = f"{safe_date}.md"
                filepath = folder / filename
                
                if filepath.exists():
                    continue
                
                try:
                    content = self.build_frontmatter(chat_type, chat_name, chat_id, day_date, len(day_messages))
                    content += f"# 📅 {day_date}\n"
                    content += f"*Всего сообщений: {len(day_messages)}*\n"
                    content += "=" * 50 + "\n"
                    
                    for msg in day_messages:
                        content += self.format_message(msg, folder)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.stats['messages'] += len(day_messages)
                except Exception as e:
                    print(f"      ❌ Ошибка дня {day_date}: {e}")
        else:
            # Старый режим: 1 сообщение = 1 файл
            for idx, msg in enumerate(messages):
                msg_id = msg.get('id')
                date_str = msg.get('date', '')
                safe_date = date_str.replace(':', '-').replace(' ', '_') if date_str else ""
                filename = f"{safe_date}_{msg_id}.md" if safe_date else f"msg_{msg_id}.md"
                filepath = folder / filename
                
                if filepath.exists():
                    continue
                
                try:
                    content = self.build_frontmatter(chat_type, chat_name, chat_id, date_str)
                    content += self.format_message(msg, folder)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    self.stats['messages'] += 1
                except Exception as e:
                    print(f"      ❌ Ошибка сообщения {msg_id}: {e}")
    
    def copy_profile_pictures(self, data: Dict):
        """🆕 Копирует фотографии профиля"""
        if not COPY_PROFILE_PICS:
            return
        
        profile_pics = data.get('profile_pictures', [])
        if not profile_pics:
            return
        
        print("\n📸 Копирование аватарок...")
        profile_dir = OUTPUT_DIR / "Profile"
        profile_dir.mkdir(exist_ok=True)
        
        for pic in profile_pics:
            photo_path = pic.get('photo')
            if photo_path and "(File not included" not in str(photo_path):
                self.copy_media_file(photo_path, "Profile")
        
        print(f"  ✅ Скопировано {len(profile_pics)} аватарок")
    
    def create_contact_notes(self, data: Dict):
        """Создает заметки для контактов"""
        if not CREATE_CONTACTS:
            return
        
        contacts = data.get('contacts', {}).get('list', [])
        if not contacts:
            return
        
        print("\n👥 Создание заметок контактов...")
        contacts_folder = OUTPUT_DIR / "Contacts"
        contacts_folder.mkdir(exist_ok=True)
        
        for contact in contacts:
            first = contact.get('first_name', '')
            last = contact.get('last_name', '')
            phone = contact.get('phone_number', '')
            date = contact.get('date', '')
            
            name = f"{first} {last}".strip()
            if not name:
                name = phone or "Unknown Contact"
            
            safe_name = self.sanitize_filename(name)
            filepath = contacts_folder / f"{safe_name}.md"
            
            if filepath.exists():
                continue
            
            content = f"# {name}\n"
            if phone:
                content += f"- **Телефон:** `{phone}`\n"
            if date:
                content += f"- **Дата добавления:** {date}\n"
            content += "\n"
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.stats['contacts'] += 1
            except Exception as e:
                print(f"  ❌ Ошибка создания контакта {name}: {e}")
        
        print(f"  ✅ Создано {self.stats['contacts']} заметок контактов")
    
    def create_index(self, data: Dict):
        """Создает индексный файл"""
        if not CREATE_INDEX:
            return
        
        chats_data = data.get('chats', {})
        chats = chats_data.get('list', []) if isinstance(chats_data, dict) else (chats_data if isinstance(chats_data, list) else [])
        
        print("\n📑 Создание индексного файла...")
        index_path = OUTPUT_DIR / "Index.md"
        
        content = "# 📱 Telegram Export\n"
        content += "Экспорт чатов из Telegram в формате Obsidian.\n\n"
        content += "## 💬 Чаты\n"
        
        chats_by_type = {
            'Saved Messages': [],
            'Personal Chats': [],
            'Groups': [],
            'Channels': [],
            'Other': []
        }
        
        for chat in chats:
            if not isinstance(chat, dict):
                continue
            
            chat_name = chat.get('name')
            if not chat_name:
                chat_name = f"Chat_{chat.get('id', 'unknown')}"
            
            chat_type = chat.get('type', 'unknown')
            safe_name = self.sanitize_filename(chat_name)
            msg_count = len(chat.get('messages', []))
            
            if chat_type == 'saved_messages':
                folder = "Saved Messages"
                chats_by_type['Saved Messages'].append((chat_name, folder, msg_count))
            elif chat_type == 'personal_chat':
                folder = f"Personal Chats/{safe_name}"
                chats_by_type['Personal Chats'].append((chat_name, folder, msg_count))
            elif chat_type in ('group', 'supergroup', 'private_supergroup', 'public_supergroup'):
                folder = f"Groups/{safe_name}"
                chats_by_type['Groups'].append((chat_name, folder, msg_count))
            elif chat_type in ('channel', 'public_channel', 'private_channel'):
                folder = f"Channels/{safe_name}"
                chats_by_type['Channels'].append((chat_name, folder, msg_count))
            else:
                folder = f"Other Chats/{safe_name}"
                chats_by_type['Other'].append((chat_name, folder, msg_count))
        
        for category, chat_list in chats_by_type.items():
            if chat_list:
                content += f"### {category}\n"
                for chat_name, folder, msg_count in sorted(chat_list):
                    content += f"- **[{chat_name}]({folder})** — {msg_count} сообщений\n"
                content += "\n"
        
        # Контакты
        contacts_folder = OUTPUT_DIR / "Contacts"
        if contacts_folder.exists():
            contacts = list(contacts_folder.glob("*.md"))
            if contacts:
                content += "## 👤 Контакты\n"
                for contact_file in sorted(contacts):
                    name = contact_file.stem
                    content += f"- [{name}](Contacts/{contact_file.name})\n"
                content += "\n"
        
        # Статистика
        content += "## 📊 Статистика\n"
        content += f"- **Всего чатов:** {len(chats)}\n"
        content += f"- **Всего сообщений:** {self.stats['messages']}\n"
        content += f"- **Всего контактов:** {self.stats['contacts']}\n"
        content += f"- **Скопировано медиа:** {self.stats['media_files']}\n"
        content += f"- **patch.txt сгенерирован:** {'✅' if self.stats['patch_generated'] else '❌'}\n"
        content += f"\n---\n*Создано: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n"
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Индексный файл создан: {index_path}")
        except Exception as e:
            print(f"  ❌ Ошибка создания индексного файла: {e}")
    
    def load_data(self) -> bool:
        """Загружает данные из JSON файла"""
        try:
            print(f"\n📂 Загрузка JSON файла: {JSON_FILE}")
            with open(JSON_FILE, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print("  ✅ JSON загружен успешно")
            return True
        except FileNotFoundError:
            print(f"  ❌ Файл {JSON_FILE} не найден!")
            return False
        except json.JSONDecodeError as e:
            print(f"  ❌ Ошибка парсинга JSON: {e}")
            return False
        except Exception as e:
            print(f"  ❌ Ошибка загрузки: {e}")
            return False
    
    def run(self):
        """Запускает процесс конвертации"""
        print("=" * 70)
        print("🚀 Telegram → Obsidian Converter")
        print("=" * 70)
        print(f"📁 JSON файл: {JSON_FILE}")
        print(f"📁 Папка экспорта: {EXPORT_BASE}")
        print(f"📁 Выходная папка: {OUTPUT_DIR}")
        print(f"📄 patch.txt: {PATCH_FILE}")
        print(f"🔄 Авто-генерация patch.txt: {'✅' if GENERATE_PATCH_FILE else '❌'}")
        print(f"🖼️  Копировать медиа: {'✅' if COPY_MEDIA else '❌'}")
        print(f"👤 Копировать аватарки: {'✅' if COPY_PROFILE_PICS else '❌'}")
        print(f"📄 Создавать frontmatter: {'✅' if CREATE_FRONTMATTER else '❌'}")
        print(f"🔒 Спойлеры как callout: {'✅' if SPOILER_AS_CALLOUT else '❌'}")
        print(f"📅 Группировка по дням: {'✅' if GROUP_BY_DAY else '❌'}")
        print("=" * 70)
        
        # 🆕 Генерируем patch.txt автоматически
        self.generate_patch_file()
        
        # Загружаем данные
        if not self.load_data():
            return
        
        # Получаем список чатов
        chats_data = self.data.get('chats', {})
        if isinstance(chats_data, dict):
            chats = chats_data.get('list', [])
            print(f"\n📋 Найдено чатов в chats.list: {len(chats)}")
        else:
            chats = chats_data if isinstance(chats_data, list) else []
            print(f"\n📋 Найдено чатов: {len(chats)}")
        
        if not chats:
            print("⚠️  Предупреждение: список чатов пуст!")
            return
        
        self.stats['chats'] = len(chats)
        
        # Обрабатываем чаты
        print("\n🔄 Обработка чатов...")
        for idx, chat in enumerate(chats, 1):
            if not isinstance(chat, dict):
                print(f"  [{idx}/{len(chats)}] Пропущен: элемент не является словарём")
                continue
            self.process_chat(chat, idx, len(chats))
        
        # Копируем аватарки
        self.copy_profile_pictures(self.data)
        
        # Создаем контакты
        self.create_contact_notes(self.data)
        
        # Создаем индекс
        self.create_index(self.data)
        
        # Итоговая статистика
        print("\n" + "=" * 70)
        print("✅ КОНВЕРТАЦИЯ ЗАВЕРШЕНА!")
        print("=" * 70)
        print(f"📊 Статистика:")
        print(f"   • Обработано чатов: {self.stats['chats']}")
        print(f"   • Создано заметок: {self.stats['messages']}")
        print(f"   • Скопировано медиа: {self.stats['media_files']}")
        print(f"   • Создано контактов: {self.stats['contacts']}")
        print(f"   • patch.txt сгенерирован: {'✅' if self.stats['patch_generated'] else '❌'}")
        print(f"\n📁 Файлы сохранены в: {OUTPUT_DIR.absolute()}")
        print("=" * 70)


def main():
    converter = TelegramToObsidian()
    converter.run()


if __name__ == "__main__":
    main()