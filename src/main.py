import logging

from telegram.ext import Application, CallbackQueryHandler, ChatMemberHandler, CommandHandler, MessageHandler, filters

from .registration_handler import RegistrationFlow
from .settings import BOT_TOKEN
from .user_storage import user_storage

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
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


async def track_chat_member_updates(update, context):
    """
    Отслеживает изменения статуса бота в чате с пользователем.
    Срабатывает когда пользователь блокирует или разблокирует бота.
    """
    result = update.my_chat_member
    user_id = result.from_user.id
    old_status = result.old_chat_member.status
    new_status = result.new_chat_member.status

    logger.info(f"Chat member update for user {user_id}: {old_status} -> {new_status}")

    # Проверяем, существует ли пользователь в БД
    user = user_storage.get_user(user_id)
    if not user:
        logger.info(f"User {user_id} not found in database, skipping status update")
        return

    # Пользователь заблокировал бота
    if new_status in ["kicked", "left"] and old_status in ["member", "administrator"]:
        logger.warning(f"User {user_id} blocked the bot")
        user_storage.update_user(user_id, "is_blocked", 1)

    # Пользователь разблокировал бота
    elif new_status in ["member", "administrator"] and old_status in ["kicked", "left"]:
        logger.info(f"User {user_id} unblocked the bot")
        user_storage.update_user(user_id, "is_blocked", 0)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.CONTACT, handle_message))
    application.add_handler(CallbackQueryHandler(registration_flow.handle_inline_query))

    # Track when users block/unblock the bot
    application.add_handler(ChatMemberHandler(track_chat_member_updates, ChatMemberHandler.MY_CHAT_MEMBER))

    # log all errors
    application.add_error_handler(error_handler)

    # Run the bot until the user presses Ctrl-C
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=["message", "callback_query", "my_chat_member"])


if __name__ == "__main__":
    main()
