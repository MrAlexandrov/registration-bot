from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from storage import storage
from settings import CANT_RIDE_USERS
from texts import TEXT_CANT_RIDE_A_TRIP

async def send_cant_ride(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user_id in CANT_RIDE_USERS:
        try:
            await context.bot.send_message(chat_id=user_id, text=TEXT_CANT_RIDE_A_TRIP)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await update.message.reply_text(f"Сообщения успешно отправлены {len(CANT_RIDE_USERS)} пользователям.")
