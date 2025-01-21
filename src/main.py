from registration_handler import registration_flow
from settings import BOT_TOKEN
from telegram.ext import Application, CommandHandler, MessageHandler, filters


async def start(update, context):
    """Обрабатывает команду /start."""
    await registration_flow.handle_command(update, context)


async def handle_message(update, context):
    """Обрабатывает сообщения пользователя."""
    await registration_flow.handle_input(update, context)


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))

    # Пользовательский ввод
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.CONTACT, handle_message))

    print("Bot started successfully!")
    application.run_polling()


if __name__ == "__main__":
    main()
