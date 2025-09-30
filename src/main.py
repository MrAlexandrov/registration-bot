import logging
import logging
from registration_handler import RegistrationFlow
from feedback_handler import FeedbackHandler
from user_storage import user_storage
from settings import BOT_TOKEN, ADMIN_STATES
from constants import *
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
logger = logging.getLogger(__name__)

registration_flow = RegistrationFlow(user_storage)
feedback_handler = FeedbackHandler(user_storage)
admin_states = [s[STATE] for s in ADMIN_STATES]


async def error_handler(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


async def start(update, context):
    """Обрабатывает команду /start."""
    await registration_flow.handle_command(update, context)


async def handle_message(update, context):
    """Обрабатывает сообщения пользователя."""
    user_id = update.message.from_user.id
    user_data = user_storage.get_user(user_id)
    current_state = user_data.get('state')

    if update.message.text == CREATE_SURVEY:
        await feedback_handler.handle_command(update, context)
    elif current_state in admin_states:
        await feedback_handler.handle_input(update, context)
    else:
        await registration_flow.handle_input(update, context)


async def handle_inline_query(update, context):
    """Обрабатывает инлайн-кнопки."""
    user_id = update.callback_query.from_user.id
    user_data = user_storage.get_user(user_id)
    current_state = user_data.get('state')
    
    action = update.callback_query.data.split('|')[0]

    if action == 'answer':
        await feedback_handler.handle_inline_query(update, context)
    elif current_state in admin_states:
        await feedback_handler.handle_inline_query(update, context)
    else:
        await registration_flow.handle_inline_query(update, context)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.CONTACT, handle_message))
    application.add_handler(CallbackQueryHandler(handle_inline_query))

    # log all errors
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    main()
