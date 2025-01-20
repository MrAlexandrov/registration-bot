from pprint import pprint
from telegram import (
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove, 
    Update,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    PicklePersistence,
    filters,
    CallbackQueryHandler,
    BasePersistence,
    PersistenceInput,
    CallbackContext
)
from logger import logger
from settings import BOT_TOKEN
from telegram.constants import ParseMode

from sqlite_persistence import SqliteUserPersistence
from message_formatter import MessageFormatter


from registration_handler import registration_flow
from user_storage import UserStorage


async def start(update, context):
    """Запускает регистрацию."""
    await registration_flow.start_registration(update, context)


async def handle_user_input(update, context):
    """Обрабатывает ввод пользователя во время регистрации."""
    await registration_flow.handle_response(update, context)


def main() -> None:   
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("register", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_user_input))

    print("Bot started successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()
