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
)
import sqlite3
import pandas as pd
from datetime import datetime
from typing import Dict
import re

from logger import logger
from keyboards import *
from texts import *
from storage import storage
from user import User
from validators import validate_date, validate_group, validate_phone
from settings import ADMIN_IDS
from filters import check_registered_filter

(WRITING_FULL_NAME, WRITING_BIRTH_DATE, WRITING_GROUP,
 WRITING_PHONE_NUMBER, WRITING_EXPECTATIONS, WRITING_FOOD_WISHES,
 FINISHED, CHANGE_DATA_OPTION) = range(8)

DB_FILE_PATH = 'users.db'
EXCEL_FILE_PATH = 'users.xlsx'


def save_user_data(context):
    user = User(
        timestamp=context.user_data.get("timestamp", str(datetime.now())),
        user_id=context.user_data.get("user_id"),
        username=context.user_data.get("username"),
        full_name=context.user_data.get("full_name", ""),
        birth_date=context.user_data.get("birth_date", ""),
        study_group=context.user_data.get("study_group", ""),
        phone_number=context.user_data.get("phone_number", ""),
        expectations=context.user_data.get("expectations", ""),
        food_wishes=context.user_data.get("food_wishes", "")
    )
    storage.save_user(user)

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def show_public_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data["user_id"]
    user_data = storage.get_user(user_id).to_public_dict()
    if user_data:
        message = (
            f"Имя: {user_data.get('full_name')}\n"
            f"Дата рождения: {user_data.get('birth_date')}\n"
            f"Группа: {user_data.get('study_group')}\n"
            f"Телефон: {user_data.get('phone_number')}\n"
            f"Ожидания: {user_data.get('expectations')}\n"
            f"Пожелания по питанию: {user_data.get('food_wishes')}"
        )
    else:
        message = "Данные о тебе не найдены"
    
    await update.message.reply_text(message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} начал взаимодействие.")
    context.user_data["user_id"] = user_id
    context.user_data["username"] = update.effective_user.username or None

    await update.message.reply_text(TEXT_HELLO)
    if storage.get_user(user_id=user_id) is None and context.user_data.get("registered") is None:
        if storage.get_user(user_id=user_id) is None:
            await update.message.reply_text(TEXT_NO_NEW_REGISTRATION)
            return
        context.user_data["timestamp"] = str(datetime.now())
        await update.message.reply_text(TEXT_ASK_FIO_FIRST_TIME, reply_markup=ReplyKeyboardRemove())
        return WRITING_FULL_NAME
    else:
        reply_text = (f"Мы уже знакомы! Чем могу помочь?")
        await update.message.reply_text(reply_text, reply_markup=main_menu_keyboard)
        return FINISHED
    
async def writing_full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("writing_full_name")
    full_name = str(update.message.text)
    context.user_data["full_name"] = full_name
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("ФИО обновлены.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text(TEXT_ASK_BIRTH_DATE_FIRST_TIME, reply_markup=ReplyKeyboardRemove())
        return WRITING_BIRTH_DATE

def format_date(date):
    day, month, year = date.split('.')
    # Форматируем день и месяц, добавляя ведущий ноль, если нужно
    day = day.zfill(2)
    month = month.zfill(2)
    return f"{day}.{month}.{year}"

async def writing_birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("writing_birth_date")
    birth_date = str(update.message.text)

    if not validate_date(birth_date):
        await update.message.reply_text(TEXT_WRONG_DATE)
        return WRITING_BIRTH_DATE
    
    formatted_birth_date = str(format_date(birth_date))

    context.user_data["birth_date"] = formatted_birth_date
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("День Рождения изменён.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text(TEXT_ASK_GROUP_FIRST_TIME, reply_markup=ReplyKeyboardRemove())
        return WRITING_GROUP

async def writing_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("writing_group")
    group = str(update.message.text)
    if not validate_group(group):
        await update.message.reply_text(TEXT_WRONG_GROUP)
        return WRITING_GROUP
    context.user_data["study_group"] = group
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Группа обновлена.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text(
            TEXT_ASK_PHONE_NUMBER_FIRST_TIME, 
            reply_markup=ask_phone_number_keyboard
        )
        return WRITING_PHONE_NUMBER
    
async def writing_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("writing_phone_number")
    if update.message.contact is not None:
        # Пользователь поделился контактом
        phone_number = str(update.message.contact.phone_number)
    else:
        # Пользователь ввёл номер вручную
        phone_number = str(update.message.text)
    # Удаляем все символы, кроме цифр
    phone_number = str(re.sub(r'\D', '', phone_number))
    if not validate_phone(phone_number):
        await update.message.reply_text(
            TEXT_WRONG_PHONE_NUMBER,
            reply_markup=ask_phone_number_keyboard
        )
        return WRITING_PHONE_NUMBER
    context.user_data["phone_number"] = phone_number
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Номер телефона обновлён.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text(TEXT_ASK_EXPECTATIONS_FIRST_TIME, reply_markup=ReplyKeyboardRemove())
        return WRITING_EXPECTATIONS
    
async def writing_expectations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("writing_expectations")
    expectations = str(update.message.text)
    context.user_data["expectations"] = expectations
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Ожидания обновлены.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text(TEXT_ASK_FOOD_WISHES_FIRST_TIME, reply_markup=answer_no_keyboard)
        return WRITING_FOOD_WISHES
    
async def writing_food_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("writing_food_wishes")
    food_wishes = str(update.message.text)
    context.user_data["food_wishes"] = food_wishes
    save_user_data(context)
    if context.user_data.get("registered"):
        await update.message.reply_text("Особенности питания обновлены.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
    else:
        context.user_data["registered"] = True
        await update.message.reply_text(
            TEXT_CONGRATULATIONS_FOR_REGISTRATION,
            reply_markup=main_menu_keyboard
        )
        await update.message.reply_text("Вот, что я о тебе знаю, если что-то не так, поправь")
        await show_public_data(update, context)

    return FINISHED

async def about_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("about_trip")
    await update.message.reply_text(TEXT_ABOUT)
    await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
    return FINISHED

async def what_to_take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("what_to_take")
    await update.message.reply_text(TEXT_WHAT_TO_TAKE)
    await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
    return FINISHED

async def change_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("change_data")
    await update.message.reply_text("Что хочешь изменить?", reply_markup=change_data_keyboard)
    return CHANGE_DATA_OPTION

async def change_data_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("change_data_option")
    choice = str(update.message.text)
    if choice == CHANGE_FIO_BUTTON:
        await update.message.reply_text(TEXT_ASK_FIO_AGAIN)
        return WRITING_FULL_NAME
    elif choice == CHANGE_BIRTH_DAY_BUTTON:
        await update.message.reply_text(TEXT_ASK_BIRTH_DATE_AGAIN)
        return WRITING_BIRTH_DATE
    elif choice == CHANGE_GROUP_BUTTON:
        await update.message.reply_text(TEXT_ASK_GROUP_AGAIN)
        return WRITING_GROUP
    elif choice == CHANGE_PHONE_NUBER_BUTTON:
        await update.message.reply_text(TEXT_ASK_PHONE_NUMBER_AGAIN, reply_markup=ask_phone_number_keyboard)
        return WRITING_PHONE_NUMBER
    elif choice == CHANGE_EXPECTATIONS_BUTTON:
        await update.message.reply_text(TEXT_ASK_EXPECTATIONS_AGAIN)
        return WRITING_EXPECTATIONS
    elif choice == CHANGE_FOOD_WISHES_BUTTON:
        await update.message.reply_text(TEXT_ASK_FOOD_WISHES_AGAIN)
        return WRITING_FOOD_WISHES
    elif choice == CHANGE_BACK:
        await update.message.reply_text("Возвращаемся назад.", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text("Пожалуйста, выбери один из вариантов.", reply_markup=change_data_keyboard)
        return CHANGE_DATA_OPTION

async def finished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("finished")
    text = str(update.message.text)
    if text == ABOUT_TRIP:
        return await about_trip(update, context)
    elif text == WHAT_TO_TAKE:
        return await what_to_take(update, context)
    elif text == CHANGE_DATA:
        return await change_data(update, context)
    elif text == SHOW_DATA:
        await show_public_data(update, context)
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text("Пожалуйста, выбери один из вариантов.", reply_markup=main_menu_keyboard)
        return FINISHED
    
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("cancel")
    await update.message.reply_text("Ты уже прошёл(ла) регистрацию. Если захочешь начать заново, отправь /start.")
    return ConversationHandler.END

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("help")
    await update.message.reply_text(TEXT_HELP)


async def send_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("send_db")
    chat_id = update.effective_chat.id
    
    try:
        # Отправляем файл
        await context.bot.send_document(chat_id=chat_id, document=open('users.db', 'rb'), filename='users.db')
        await update.message.reply_text("База данных отправлена.")
    except Exception as e:
        await update.message.reply_text(f"Не удалось отправить файл: {e}")

def export_db_to_excel():
    logger.debug("export_db_to_excel")
    # Подключаемся к базе данных
    conn = sqlite3.connect(DB_FILE_PATH)
    
    # Выполняем запрос к таблице (замените 'users' на имя вашей таблицы)
    df = pd.read_sql_query("SELECT * FROM users", conn)

    # Сохраняем DataFrame в Excel-файл
    df.to_excel(EXCEL_FILE_PATH, index=False)

    # Закрываем соединение с базой данных
    conn.close()

async def send_excel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("send_excel")
    chat_id = update.effective_chat.id

    try:
        # Экспортируем базу данных в файл Excel
        export_db_to_excel()

        # Отправляем файл Excel
        await context.bot.send_document(chat_id=chat_id, document=open(EXCEL_FILE_PATH, 'rb'), filename='users.xlsx')
        await update.message.reply_text("Данные базы отправлены в формате Excel.")
    except Exception as e:
        await update.message.reply_text(f"Не удалось отправить файл: {e}")

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("add_admin")

    # Получаем список аргументов команды
    try:
        new_admin_id = int(context.args[0])  # context.args[0] содержит первый аргумент после команды
        if new_admin_id not in ADMIN_IDS:
            ADMIN_IDS.append(new_admin_id)
            await update.message.reply_text(f"Добавлен администратор с id = {new_admin_id}")
        else:
            await update.message.reply_text(f"Администратор с id = {new_admin_id} уже существует")
    except (IndexError, ValueError):
        await update.message.reply_text("Ошибка: введите корректный ID")

async def delete_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("delete_admin")

    # Получаем список аргументов команды
    try:
        admin_id_to_delete = int(context.args[0])  # context.args[0] содержит первый аргумент после команды
        if admin_id_to_delete in ADMIN_IDS:
            ADMIN_IDS.remove(admin_id_to_delete)
            await update.message.reply_text(f"Удален администратор с id = {admin_id_to_delete}")
        else:
            await update.message.reply_text(f"Администратора с id = {admin_id_to_delete} не существует")
    except (IndexError, ValueError):
        await update.message.reply_text("Ошибка: введите корректный ID")


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        WRITING_FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_full_name)],
        WRITING_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_group)],
        WRITING_BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_birth_date)],
        WRITING_PHONE_NUMBER: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, writing_phone_number),
            MessageHandler(filters.CONTACT, writing_phone_number)
        ],
        WRITING_EXPECTATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_expectations)],
        WRITING_FOOD_WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_food_wishes)],
        FINISHED: [MessageHandler(filters.TEXT & ~filters.COMMAND, finished)],
        CHANGE_DATA_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_data_option)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    name="my_conversation",
    persistent=True
)