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
)
# from keyboards import *
from logger import logger
from settings import BOT_TOKEN
# from texts import *
from filters import check_admin_filter
from handle_registration import show_users, send_db, send_excel, conv_handler


def main() -> None:
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help))

    application.add_handler(CommandHandler("show_users", show_users, filters=check_admin_filter))
    application.add_handler(CommandHandler("send_db", send_db, filters=check_admin_filter))
    application.add_handler(CommandHandler('send_excel', send_excel, filters=check_admin_filter))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()