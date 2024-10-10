from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from settings import ALL_RIDERS

async def send_message_all_riders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_text = " ".join(context.args[0:])
    for user_id in ALL_RIDERS:
        try:
            await context.bot.send_message(chat_id=user_id, text=message_text)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await update.message.reply_text(f"Сообщения успешно отправлены {len(ALL_RIDERS)} пользователям.")
