from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import asyncio
from settings import ALL_RIDERS, ROOT_ID
from keyboards import yes_no_keyboard
from texts import TEXT_ARE_YOU_READY

async def ask_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for user_id in ALL_RIDERS:
        try:
            await context.bot.send_message(
                chat_id=user_id, 
                text=TEXT_ARE_YOU_READY, 
                parse_mode='HTML', 
                reply_markup=yes_no_keyboard
            )
        except Exception as e:
            print(f"Не удалось отправить сообщение пользователю {user_id}: {e}")

    await update.message.reply_text(f"Сообщения успешно отправлены {len(ALL_RIDERS)} пользователям.")

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

    await query.edit_message_reply_markup(reply_markup=None)

    # Определяем ответ пользователя
    if callback_data == 'yes':
        answer = 'Да'
        await context.bot.send_message(
            chat_id=user_id, 
            text="Будем ждать! ❤️",
            parse_mode='HTML',
            disable_web_page_preview=True
        )
    elif callback_data == 'no':
        answer = 'Нет'
        await context.bot.send_message(chat_id=user_id, text="Хорошо, спасибо за ответ!")
        await context.bot.send_message(
            chat_id=ROOT_ID, 
            text=f"Пользователь с id = <code>{user_id}</code> отказался ехать на выезд",
            parse_mode='HTML'
        )
    else:
        return  # Если неизвестное значение, ничего не делаем


    # Сохраняем информацию об ответе в файл
    save_answer(user_id, answer)

    # Уведомляем пользователя, что его ответ сохранен
    # await query.edit_message_text(text=f"Я записал, твой ответ: {answer}")