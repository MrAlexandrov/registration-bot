from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from settings import AGREED_USERS
from keyboards import yes_no_keyboard

async def ask_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user_id in AGREED_USERS:
        try:
            await context.bot.send_message(chat_id=user_id, text="И в последний раз узнаю, точно ли ты поедешь на Пионерский выезд? (Если что, пока тестирую на зареганых оргах, тыкни что-нибудь)", reply_markup=yes_no_keyboard)
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await update.message.reply_text(f"Сообщения успешно отправлены {len(AGREED_USERS)} пользователям.")

def save_answer(user_id: int, answer: str):
    # Открываем файл для записи (в режиме добавления)
    with open('answer_file.txt', 'a') as file:
        file.write(f"{user_id} - {answer}\n")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()  # Подтверждаем получение callback'а

    # Получаем данные callback_data из нажатой кнопки
    callback_data = query.data
    user_id = query.from_user.id

    # Определяем ответ пользователя
    if callback_data == 'yes':
        answer = 'Да'
        await context.bot.send_message(chat_id=user_id, text="Отлично!")
    elif callback_data == 'no':
        answer = 'Нет'
        await context.bot.send_message(chat_id=user_id, text="Хорошо, спасибо за ответ!")
    else:
        return  # Если неизвестное значение, ничего не делаем

    await query.edit_message_reply_markup(reply_markup=None)

    # Сохраняем информацию об ответе в файл
    save_answer(user_id, answer)

    # Уведомляем пользователя, что его ответ сохранен
    await query.edit_message_text(text=f"Ваш ответ: {answer}")