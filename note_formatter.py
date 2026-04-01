import os
from datetime import datetime
import re

class NoteFormatter:
    def __init__(self, config):
        self.config = config
    
    def sanitize_filename(self, text):
        """Очищает текст для использования в имени файла"""
        # Убираем недопустимые символы
        text = re.sub(r'[<>:"/\\|?*]', '_', text)
        # Ограничиваем длину
        if len(text) > 100:
            text = text[:100]
        return text.strip()
    
    def format_note(self, message, channel_title):
        """Форматирует сообщение в markdown"""
        content_parts = []
        
        # Frontmatter (YAML)
        frontmatter = []
        frontmatter.append('---')
        frontmatter.append(f'title: "{self._extract_title(message)}"')
        frontmatter.append(f'channel: "{channel_title}"')
        frontmatter.append(f'channel_username: "{message.chat.username}"')
        
        if self.config['INCLUDE_DATE'] and message.date:
            frontmatter.append(f'date: {message.date.strftime(self.config["DATE_FORMAT"])}')
            frontmatter.append(f'timestamp: {int(message.date.timestamp())}')
        
        frontmatter.append(f'message_id: {message.id}')
        
        if message.media_unread:
            frontmatter.append('has_media: true')
        
        frontmatter.append('---')
        frontmatter.append('')
        content_parts.extend(frontmatter)
        
        # Заголовок (если это не медиа-сообщение без текста)
        if message.text:
            title = self._extract_title(message)
            if title and len(title) < 60:
                content_parts.append(f'# {title}')
                content_parts.append('')
        
        # Текст сообщения
        if message.text:
            content_parts.append(message.text)
            content_parts.append('')
        
        # Информация о медиа
        if message.media:
            media_info = self._format_media_info(message)
            if media_info:
                content_parts.append('## 📎 Медиа')
                content_parts.append(media_info)
                content_parts.append('')
        
        # Ссылка на сообщение
        if self.config['INCLUDE_LINK']:
            message_link = f'https://t.me/{message.chat.username}/{message.id}'
            content_parts.append(f'---')
            content_parts.append(f'🔗 [Открыть в Telegram]({message_link})')
        
        return '\n'.join(content_parts)
    
    def _extract_title(self, message):
        """Извлекает заголовок из сообщения"""
        if not message.text:
            return f"Сообщение от {message.date.strftime('%Y-%m-%d')}"
        
        # Первая строка как заголовок
        first_line = message.text.split('\n')[0].strip()
        # Ограничиваем длину
        if len(first_line) > 50:
            first_line = first_line[:47] + '...'
        return first_line
    
    def _format_media_info(self, message):
        """Форматирует информацию о медиафайлах"""
        media_info = []
        
        if message.photo:
            media_info.append(f'- 📷 Фото (ID: {message.photo.id})')
        
        if message.video:
            duration = message.video.duration if hasattr(message.video, 'duration') else 'неизвестно'
            media_info.append(f'- 🎥 Видео ({duration} сек)')
        
        if message.document:
            file_name = getattr(message.document, 'attributes', [{}])[0].get('file_name', 'файл')
            media_info.append(f'- 📄 Документ: {file_name}')
        
        if message.voice:
            duration = message.voice.duration if hasattr(message.voice, 'duration') else 'неизвестно'
            media_info.append(f'- 🎙️ Голосовое ({duration} сек)')
        
        if message.audio:
            media_info.append(f'- 🎵 Аудио')
        
        return '\n'.join(media_info) if media_info else None
    
    def get_file_path(self, message, channel_title):
        """Определяет путь для сохранения файла"""
        date_str = message.date.strftime('%Y%m%d_%H%M%S')
        title = self._extract_title(message)
        safe_title = self.sanitize_filename(title)
        
        filename = f"{date_str}_{safe_title}.md"
        
        if self.config['ORGANIZE_BY_CHANNEL']:
            channel_folder = self.sanitize_filename(channel_title)
            return os.path.join(channel_folder, filename)
        else:
            return filename