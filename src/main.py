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
from logger import logger
from settings import BOT_TOKEN
from filters import check_admin_filter, check_root_filter
from handle_registration import send_db, send_excel, conv_handler, help,\
add_admin, delete_admin


def main() -> None:
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help))

    application.add_handler(CommandHandler("send_db",       send_db,        filters=check_admin_filter))
    application.add_handler(CommandHandler('send_excel',    send_excel,     filters=check_admin_filter))
    application.add_handler(CommandHandler('add_admin',     add_admin,      filters=check_root_filter))
    application.add_handler(CommandHandler('delete_admin',  delete_admin,   filters=check_root_filter))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()