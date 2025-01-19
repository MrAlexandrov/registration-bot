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

from sqlite_persistence import SqlitePersistence
from message_formatter import MessageFormatter

from registration_flow import registration_flow

async def show_data(update: Update, context: CallbackContext) -> None:
    """Отправляем сохранённые сообщения с форматированием"""
    
    def _read_messages(chat_messages):
        return '\n'.join([f'{x["message_ts"]}: {x["message"]}' for x in chat_messages])

    messages = [f"\n{key}:\n{_read_messages(value)}" for key, value in context.chat_data.items()]
    facts = '\n'.join(messages) if messages else "No messages found."

    formatted_text = MessageFormatter.get_escaped_text(update.message, parse_mode=ParseMode.MARKDOWN_V2)
    await update.message.reply_text(formatted_text, parse_mode=ParseMode.MARKDOWN_V2)


async def save_message(update: Update, context: CallbackContext) -> None:
    """Сохраняем сообщение с форматированием в контекст и базу данных"""
    formatted_text = MessageFormatter.get_escaped_text(update.message, parse_mode=ParseMode.MARKDOWN_V2)

    if 'messages' not in context.chat_data:
        context.chat_data['messages'] = []

    context.chat_data['messages'].append({
        'message': formatted_text,
        'message_ts': update.message.date.timestamp()
    })


async def echo(update: Update, context) -> None:
    parse_mode = ParseMode.MARKDOWN_V2
    formatted_text = MessageFormatter.get_escaped_text(update.message, parse_mode=parse_mode)

    # Отправляем сообщение обратно, сохраняя форматирование
    await update.message.reply_text(
        formatted_text,
        parse_mode=parse_mode
    )

async def profile(update: Update, context: CallbackContext):
    """Отображает профиль пользователя."""
    name = context.user_data.get("name", "Неизвестно")
    phone = context.user_data.get("phone", "Неизвестно")
    await update.message.reply_text(f"👤 Твой профиль:\nИмя: {name}\nТелефон: {phone}")


def main() -> None:
    # persistence = SqlitePersistence()
    # application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()
    application = Application.builder().token(BOT_TOKEN).build()

    registration_handler = ConversationHandler(
        entry_points=[CommandHandler("register", registration_flow.start_registration)],
        states={
            "ask_name": [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: registration_flow.run_step(u, c, "ask_name"))],
            "ask_contact": [MessageHandler(filters.TEXT & ~filters.COMMAND, lambda u, c: registration_flow.run_step(u, c, "ask_contact"))],
        },
        fallbacks=[CommandHandler("cancel", registration_flow.cancel)],
        name="registration_conversation",
        # persistent=True,
    )

    application.add_handler(registration_handler)
    application.add_handler(CommandHandler("profile", profile))


    logger.info("Bot started successfully!")
    application.run_polling()

if __name__ == "__main__":
    main()
