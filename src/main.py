# import json
from datetime import datetime
from pprint import pprint
from typing import Dict
from telegram import (
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove, 
    Update,
    KeyboardButton,             # for contact  
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
from keyboards import *
from logger import logger
from settings import BOT_TOKEN, SPREADSHEET_ID, GOOGLE_CREDENTIALS_FILE, FIELDNAMES
# from state_manager import get_user_state, set_user_state, load_scenario
from storage import CSVFileStorage, GoogleSheetsStorage, SQLiteStorage, CombinedStorage
from user import User
from texts import TEXT_HELLO, TEXT_ABOUT, TEXT_WHAT_TO_TAKE

storage = CombinedStorage(
    csv_file_name="users.csv",
    credentials_file=GOOGLE_CREDENTIALS_FILE,
    spreadsheet_id=SPREADSHEET_ID,
    fieldnames=FIELDNAMES,
    debug_mode=False,
    # use_sqlite=True,  # Включаем SQLite
    # sqlite_db_path="users.db"  # Путь к SQLite базе данных
)

# WRITING_FIRST_NAME = "Заполнение имени"
# WRITING_LAST_NAME = "Заполнение фамилии"
# WRITING_PATRONYMIC = "Заполнение отчства"
# WRITING_GROUP = "Заполнение группы"
# WRITING_PHONE_NUMBER = "Заполнение номера телефона"
# WRITING_EXPECTATIONS = "Заполнение ожиданий"
# WRITING_FOOD_WISHES = "Заполнение особенностей питания"
# FINISHED = "Регистрация закончена"

(WRITING_FIRST_NAME, WRITING_LAST_NAME, WRITING_PATRONYMIC, WRITING_GROUP,
 WRITING_PHONE_NUMBER, WRITING_EXPECTATIONS, WRITING_FOOD_WISHES,
 FINISHED, CHANGE_DATA_OPTION) = range(9)

# ABOUT_TRIP = "O выезде"
# WHAT_TO_TAKE = "Что взять?"
# CHANGE_DATA = "Изменить данные"

CALLBACK_WRITING_FIRST_NAME = WRITING_LAST_NAME
CALLBACK_WRITING_LAST_NAME = WRITING_PATRONYMIC
CALLBACK_WRITING_PATRONYMIC = WRITING_GROUP
CALLBACK_WRITING_GROUP = WRITING_PHONE_NUMBER
CALLBACK_WRITING_PHONE_NUMBER = WRITING_EXPECTATIONS
CALLBACK_WRITING_EXPECTATIONS = WRITING_FOOD_WISHES
CALLBACK_WRITING_FOOD_WISHES = FINISHED
CALLBACK_FINISHED = FINISHED

ABOUT_TRIP_CALLBACK = FINISHED
WHAT_TO_TAKE_CALLBACK = FINISHED
CHANGE_DATA_CALLBACK = FINISHED


# ABOUT_TRIP = "O выезде"
# WHAT_TO_TAKE = "Что взять?"
# CHANGE_DATA = "Изменить данные"

def save_user_data(context):
    user = User(
        timestamp=context.user_data.get("timestamp", str(datetime.now())),
        user_id=context.user_data.get("user_id"),
        username=context.user_data.get("username"),
        first_name=context.user_data.get("first_name", ""),
        last_name=context.user_data.get("last_name", ""),
        patronymic=context.user_data.get("patronymic", ""),
        study_group=context.user_data.get("study_group", ""),
        phone_number=context.user_data.get("phone_number", ""),
        expectations=context.user_data.get("expectations", ""),
        food_wishes=context.user_data.get("food_wishes", "")
    )
    storage.save_user(user)


# async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
#     user_id = update.effective_user.id
#     logger.info(f"Пользователь {user_id} начал взаимодействие.")
#     context.user_data["user_id"] = user_id
#     context.user_data["username"] = update.effective_user.username or None

#     await update.message.reply_text(TEXT_HELLO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"Пользователь {user_id} начал взаимодействие.")
    context.user_data["user_id"] = user_id
    context.user_data["username"] = update.effective_user.username or None

    await update.message.reply_text(TEXT_HELLO)
    if context.user_data.get("registered"):
        reply_text = (
            f"Мы уже знакомы, {context.user_data.get('first_name')}! Чем могу помочь?"
        )
        await update.message.reply_text(reply_text, reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        context.user_data["timestamp"] = str(datetime.now())
        reply_text = "Давай знакомиться! Напиши, пожалуйста, своё имя:"
        await update.message.reply_text(reply_text)
        return WRITING_FIRST_NAME

async def writing_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["first_name"] = text
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Имя обновлено.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text(f"Отлично, {text}! А теперь введи свою фамилию:")
        return WRITING_LAST_NAME

async def writing_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["last_name"] = text
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Фамилия обновлена.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text("А теперь введи своё отчество:")
        return WRITING_PATRONYMIC

async def writing_patronymic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["patronymic"] = text
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Отчество обновлено.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text("А теперь введи свою группу:")
        return WRITING_GROUP

ask_phone_number = KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)
markup_ask_phone_number = ReplyKeyboardMarkup([[ ask_phone_number ]], one_time_keyboard=True)

async def writing_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["study_group"] = text
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Группа обновлена.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text(
            "Осталось совсем немного, теперь мне нужен твой номер телефона", 
            reply_markup=markup_ask_phone_number
        )
        return WRITING_PHONE_NUMBER

async def writing_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact is not None:
        # Пользователь поделился контактом
        phone_number = update.message.contact.phone_number
    else:
        # Пользователь ввёл номер вручную
        phone_number = update.message.text
    context.user_data["phone_number"] = phone_number
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Номер телефона обновлён.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text("Что ты ожидаешь от выезда?", reply_markup=ReplyKeyboardRemove())
        return WRITING_EXPECTATIONS

answer_no = ["Нет"]
markup_answer_no = ReplyKeyboardMarkup([answer_no], one_time_keyboard=True)

async def writing_expectations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["expectations"] = text
    if context.user_data.get("registered"):
        save_user_data(context)
        await update.message.reply_text("Ожидания обновлены.")
        await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text("Есть ли у тебя аллергия на еду?", reply_markup=markup_answer_no)
        return WRITING_FOOD_WISHES

async def writing_food_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["food_wishes"] = text
    context.user_data["registered"] = True
    save_user_data(context)
    await update.message.reply_text(
        "Поздравляю! Теперь ты зарегистрирован(а) на Пионерский выезд!",
        reply_markup=main_menu_keyboard
    )
    return FINISHED

async def about_trip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_ABOUT)
    await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
    return FINISHED

async def what_to_take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(TEXT_WHAT_TO_TAKE)
    await update.message.reply_text("Чем ещё могу помочь?", reply_markup=main_menu_keyboard)
    return FINISHED

change_data_keyboard = [
    ["Имя", "Фамилию"],
    ["Отчество", "Группy"],
    ["Номер телефона", "Ожидания"],
    ["Особенности питания", "Назад"]
]
markup_change_data = ReplyKeyboardMarkup(change_data_keyboard, one_time_keyboard=True)

async def change_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Что ты хочешь изменить?", reply_markup=markup_change_data)
    return CHANGE_DATA_OPTION

async def change_data_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text
    if choice == "Имя":
        await update.message.reply_text("Введите новое имя:")
        return WRITING_FIRST_NAME
    elif choice == "Фамилию":
        await update.message.reply_text("Введите новую фамилию:")
        return WRITING_LAST_NAME
    elif choice == "Отчество":
        await update.message.reply_text("Введите новое отчество:")
        return WRITING_PATRONYMIC
    elif choice == "Группy":
        await update.message.reply_text("Введите новую группу:")
        return WRITING_GROUP
    elif choice == "Номер телефона":
        await update.message.reply_text("Введите новый номер телефона:", reply_markup=markup_ask_phone_number)
        return WRITING_PHONE_NUMBER
    elif choice == "Ожидания":
        await update.message.reply_text("Введите новые ожидания:")
        return WRITING_EXPECTATIONS
    elif choice == "Особенности питания":
        await update.message.reply_text("Введите новые особенности питания:")
        return WRITING_FOOD_WISHES
    elif choice == "Назад":
        await update.message.reply_text("Возвращаемся назад.", reply_markup=main_menu_keyboard)
        return FINISHED
    else:
        await update.message.reply_text("Пожалуйста, выбери один из вариантов.", reply_markup=markup_change_data)
        return CHANGE_DATA_OPTION

async def finished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == ABOUT_TRIP:
        return await about_trip(update, context)
    elif text == WHAT_TO_TAKE:
        return await what_to_take(update, context)
    elif text == CHANGE_DATA:
        return await change_data(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выбери один из вариантов.", reply_markup=main_menu_keyboard)
        return FINISHED

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the gathered info."""
    await update.message.reply_text(
        f"Вот, что я о тебе знаю: {facts_to_str(context.user_data)}"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ты уже прошёл(ла) регистрацию. Если захочешь начать заново, отправь /start.")
    return ConversationHandler.END

async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = storage.sqlite_storage.get_all_users()
    if users:
        users_str = "\n\n".join(str(user) for user in users)  # Преобразуем каждого пользователя в строку
    else:
        users_str = "No users found."
    
    await update.message.reply_text(users_str)
    return FINISHED

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WRITING_FIRST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_first_name)],
            WRITING_LAST_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_last_name)],
            WRITING_PATRONYMIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_patronymic)],
            WRITING_GROUP: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_group)],
            WRITING_PHONE_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_phone_number),
                MessageHandler(filters.CONTACT, writing_phone_number)
            ],
            WRITING_EXPECTATIONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_expectations)],
            WRITING_FOOD_WISHES: [MessageHandler(filters.TEXT & ~filters.COMMAND, writing_food_wishes)],
            FINISHED: [MessageHandler(filters.TEXT & ~filters.COMMAND, finished)],
            # ABOUT_TRIP: [MessageHandler(filters.Regex(f"^{ABOUT_TRIP}$"), about_trip)],
            # WHAT_TO_TAKE: [MessageHandler(filters.Regex(f"^{WHAT_TO_TAKE}$"), what_to_take)],
            # CHANGE_DATA: [MessageHandler(filters.Regex(f"^{CHANGE_DATA}$"), change_data)],
            CHANGE_DATA_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, change_data_option)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        name="my_conversation",
        persistent=True
    )

    application.add_handler(conv_handler)

    # application.add_handler(CommandHandler("start", start))

    application.add_handler(CommandHandler("show_users", show_users))

    show_data_handler = CommandHandler("show_data", show_data)
    application.add_handler(show_data_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()