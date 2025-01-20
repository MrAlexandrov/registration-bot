from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from registration_handler import registration_flow
from user_storage import user_storage
from settings import BOT_TOKEN


async def start(update, context):
    """Запускает регистрацию."""
    await registration_flow.start_registration(update, context)


async def handle_message(update, context):
    """Обрабатывает сообщения пользователя в процессе регистрации."""
    user_id = update.message.from_user.id
    user = user_storage.get_user(user_id)

    if user and user["state"] in registration_flow.steps:
        # Если пользователь в процессе регистрации, обработать шаг
        await registration_flow.handle_registration_step(update, context)
    else:
        # Если пользователь уже зарегистрирован или не начинал регистрацию
        await update.message.reply_text("Вы уже зарегистрированы или не начали регистрацию. Введите /start для начала.")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    main()
