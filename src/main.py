import logging
import logging
from registration_handler import RegistrationFlow
from user_storage import user_storage
from settings import BOT_TOKEN
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

registration_flow = RegistrationFlow(user_storage)


async def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def start(update, context):
    """Обрабатывает команду /start."""
    await registration_flow.handle_command(update, context)


async def handle_message(update, context):
    """Обрабатывает сообщения пользователя."""
    await registration_flow.handle_input(update, context)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.CONTACT, handle_message))
    application.add_handler(CallbackQueryHandler(registration_flow.handle_inline_query))

    # log all errors
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    main()
