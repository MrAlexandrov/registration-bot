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
)
from logger import logger
from settings import BOT_TOKEN
from filters import check_admin_filter, check_root_filter
from handle_registration import send_db, send_excel, conv_handler, help,\
add_admin, delete_admin
from handle_send_message import send_message
from handle_ask_again import ask_again, button_handler
from handle_send_cant_ride import send_cant_ride
from handle_send_cant_ride_missed import send_cant_ride_missed


def main() -> None:
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('help',              help))

    application.add_handler(CommandHandler('send_db',           send_db,            filters=check_admin_filter))
    application.add_handler(CommandHandler('send_excel',        send_excel,         filters=check_admin_filter))
    application.add_handler(CommandHandler('add_admin',         add_admin,          filters=check_root_filter))
    application.add_handler(CommandHandler('delete_admin',      delete_admin,       filters=check_root_filter))

    application.add_handler(CommandHandler('send_message',      send_message,       filters=check_admin_filter))

    application.add_handler(CommandHandler('ask_again',         ask_again,          filters=check_admin_filter))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.add_handler(CommandHandler('send_cant_ride',    send_cant_ride,     filters=check_admin_filter))
    application.add_handler(CommandHandler('send_cant_ride_missed', send_cant_ride_missed, filters=check_admin_filter))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()