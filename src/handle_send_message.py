from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from storage import storage

async def send_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что у команды есть аргументы
    if len(context.args) < 2:
        await update.message.reply_text("Пожалуйста, используйте команду в формате:\n/send_message <user_id> <сообщение>")
        return

    # Получаем user_id из первого аргумента
    try:
        recipient_id = int(context.args[0])  # Преобразуем в int, чтобы убедиться, что это id
    except ValueError:
        await update.message.reply_text("Ошибка: user_id должен быть числом.")
        return

    # Собираем сообщение из остальных аргументов
    message_text = " ".join(context.args[1:])
    
    # Проверяем, существует ли пользователь с таким ID в базе данных
    # conn = sqlite3.connect(DB_FILE_PATH)
    # cursor = conn.cursor()
    # cursor.execute("SELECT id FROM users WHERE id=?", (recipient_id,))
    # user = cursor.fetchone()
    # conn.close()

    user = storage.get_user(recipient_id)

    if not user:
        await update.message.reply_text(f"Пользователь с id '{recipient_id}' не найден.")
        return

    # Отправляем сообщение пользователю
    try:
        await context.bot.send_message(chat_id=recipient_id, text=message_text)
        await update.message.reply_text(f"Сообщение успешно отправлено пользователю с ID {recipient_id}.")
    except Exception as e:
        await update.message.reply_text(f"Не удалось отправить сообщение: {e}")
