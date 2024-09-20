# bot/main.py

import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from bot.config import BOT_TOKEN
from bot.handlers.registration import registration_handlers
from bot.handlers.admin import admin_handlers
from bot.handlers.common import common_handlers
from bot.middlewares.access_control import AccessControlMiddleware
from bot.database.db import init_db

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update: ContextTypes.DEFAULT_TYPE, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обработчик команды /start"""
    await update.message.reply_text("Добро пожаловать! Используйте команды для взаимодействия с ботом.")

def main():
    """Основная функция для запуска бота."""
    # Инициализация базы данных
    init_db()

    # Создание приложения бота
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    # Добавление промежуточного слоя для контроля доступа
    application.add_middleware(AccessControlMiddleware())

    # Регистрация обработчиков команд
    application.add_handler(CommandHandler("start", start))

    # Регистрация обработчиков регистрации
    for handler in registration_handlers:
        application.add_handler(handler)

    # Регистрация административных обработчиков
    for handler in admin_handlers:
        application.add_handler(handler)

    # Регистрация общих обработчиков
    for handler in common_handlers:
        application.add_handler(handler)

    # Запуск бота
    logger.info("Бот запущен и готов к работе.")
    application.run_polling()

if __name__ == '__main__':
    main()
