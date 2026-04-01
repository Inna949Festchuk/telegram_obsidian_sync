#!/usr/bin/env python3
"""
BotPhazer — Telegram бот для проекта Telegram to Obsidian Converter
Безопасная версия для публикации в каталогах ботов (без массовых рассылок)
"""
import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# ===================== НАСТРОЙКИ =====================
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Установите: pip install python-dotenv")

BOT_TOKEN = os.getenv('BOTPHAZER_TOKEN', '')
GITHUB_URL = os.getenv('GITHUB_URL', 'https://github.com/Inna949Festchuk/telegram_obsidian_sync')
README_URL = os.getenv('README_URL', 'https://github.com/Inna949Festchuk/telegram_obsidian_sync/blob/main/README.md')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='botphazer.log'
)
logger = logging.getLogger(__name__)


# ===================== ОБРАБОТЧИКИ КОМАНД =====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """👋 Обработчик команды /start"""
    user = update.effective_user
    
    welcome_text = f"""
👋 Привет, {user.first_name}!

Я — бот проекта **Telegram to Obsidian Converter**

📱 Конвертирует экспорт Telegram в заметки Obsidian с полной поддержкой медиафайлов!

✨ **Возможности:**
• 📝 Конвертация сообщений в Markdown
• 🖼️ Копирование фото, видео, документов
• 👥 Экспорт контактов
• 📅 Группировка по дням
• 📊 YAML frontmatter для аналитики

Выберите действие ниже 👇
    """
    
    keyboard = [
        [InlineKeyboardButton("📦 Скачать на GitHub", url=GITHUB_URL)],
        [InlineKeyboardButton("📖 Документация", url=README_URL)],
        [InlineKeyboardButton("❓ Помощь", callback_data='help')],
    ]
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    logger.info(f"User {user.id} (@{user.username}) started the bot")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📚 Обработчик команды /help"""
    help_text = """
📚 **Справка по боту**

**Команды:**
/start — Приветственное сообщение
/github — Ссылка на GitHub проект
/help — Эта справка
/feedback — Оставить отзыв

**О проекте:**
Telegram to Obsidian Converter — Python скрипт для конвертации экспорта Telegram в формат Obsidian.

🔗 GitHub: {github}
📖 Docs: {readme}

**Вопросы?** Пишите: @Dilmah949
    """.format(github=GITHUB_URL, readme=README_URL)
    
    keyboard = [
        [InlineKeyboardButton("⭐ Поддержать проект", url=GITHUB_URL)],
    ]
    
    await update.message.reply_text(
        help_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    logger.info(f"User {update.effective_user.id} requested help")


async def github_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📦 Обработчик команды /github"""
    user = update.effective_user
    
    github_text = f"""
🎉 **Telegram to Obsidian Converter**

{user.first_name}, спасибо за интерес к проекту!

📦 **GitHub:** {GITHUB_URL}

📖 **Документация:** {README_URL}

🚀 **Быстрый старт:**
1. Экспортируй данные из Telegram Desktop
2. Настрой .env файл
3. Запусти: `python telegram_to_obsidian.py`
4. Открой папку в Obsidian!

💡 **Совет:** Поддержите проект ⭐ на GitHub!
    """
    
    keyboard = [
        [InlineKeyboardButton("⭐ Звезда на GitHub", url=GITHUB_URL)],
        [InlineKeyboardButton("📖 Читать README", url=README_URL)],
        [InlineKeyboardButton("🐛 Сообщить о баге", url=f"{GITHUB_URL}/issues")],
    ]
    
    await update.message.reply_text(
        github_text,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    
    logger.info(f"User {update.effective_user.id} requested GitHub link")


async def feedback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """💬 Обработчик команды /feedback"""
    feedback_text = """
💬 **Оставить отзыв**

Спасибо что хотите поделиться мнением!

**Куда писать:**
• Telegram: @Dilmah949
• GitHub Issues: {github}/issues
• Email: festchuk@yandex.ru

**Что указать:**
1. Версия Python
2. ОС (Windows/Mac/Linux)
3. Описание проблемы или предложения
    """.format(github=GITHUB_URL)
    
    await update.message.reply_text(feedback_text, parse_mode='Markdown')
    logger.info(f"User {update.effective_user.id} requested feedback info")


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """🔘 Обработчик нажатий на кнопки"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        await help_command(update, context)
    elif query.data == 'github':
        await github_command(update, context)
    
    logger.info(f"Callback {query.data} from user {query.from_user.id}")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """❓ Обработчик неизвестных команд"""
    await update.message.reply_text(
        "❌ Неизвестная команда. Используйте /help для справки."
    )


async def track_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Трекинг активности (для статистики)"""
    if update.effective_user:
        logger.info(f"Activity from user {update.effective_user.id} (@{update.effective_user.username})")


# ===================== НАСТРОЙКА БОТА =====================

async def post_init(application: Application):
    """Настройка команд бота после инициализации"""
    await application.bot.set_my_commands([
        BotCommand("start", "👋 Запустить бота"),
        BotCommand("github", "📦 Ссылка на GitHub"),
        BotCommand("help", "📚 Справка"),
        BotCommand("feedback", "💬 Оставить отзыв"),
    ])
    
    logger.info("Bot commands configured")


# ===================== ЗАПУСК =====================

def main():
    """Запуск бота"""
    if not BOT_TOKEN:
        print("❌ Ошибка: BOT_TOKEN не настроен!")
        print("   Получите токен у @BotFather")
        print("   Добавьте в .env: BOTPHAZER_TOKEN=your_token")
        return
    
    print("=" * 60)
    print("🤖 BotPhazer — Telegram to Obsidian Bot")
    print("=" * 60)
    print(f"📦 GitHub: {GITHUB_URL}")
    print(f"📖 Docs: {README_URL}")
    print("=" * 60)
    print("✅ Бот запущен и ожидает команды...")
    print("   Нажмите Ctrl+C для остановки")
    print("=" * 60)
    
    # Создание приложения
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("github", github_command))
    application.add_handler(CommandHandler("feedback", feedback_command))
    application.add_handler(CommandHandler("stats", stats_command) if ADMIN_ID else None)
    
    # Обработчик кнопок
    application.add_callback_handler(button_callback)
    
    # Обработчик неизвестных команд
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    
    # Трекинг активности
    application.add_handler(MessageHandler(filters.ALL, track_user))
    
    # Запуск polling
    application.run_polling(allowed_updates=Update.ALL_TYPES)


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """📊 Статистика (только для администратора)"""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Доступ запрещён")
        return
    
    stats_text = f"""
📊 **Статистика бота**

Время работы: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Версия: 1.0.0

Полная статистика в логе: botphazer.log
    """
    
    await update.message.reply_text(stats_text, parse_mode='Markdown')


if __name__ == "__main__":
    main()