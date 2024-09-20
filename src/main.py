# import json
# from pprint import pprint
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
from settings import BOT_TOKEN, SPREADSHEET_ID, GOOGLE_CREDENTIALS_FILE, FIELDNAMES
# from bot_logging import logger
# from state_manager import get_user_state, set_user_state, load_scenario
from storage import CSVFileStorage, GoogleSheetsStorage, UserStorage, CombinedStorage
# from user import User

WRITING_FIRST_NAME = "Заполнение имени"
WRITING_LAST_NAME = "Заполнение фамилии"
WRITING_PATRONYMIC = "Заполнение отчства"
WRITING_GROUP = "Заполнение группы"
WRITING_PHONE_NUMBER = "Заполнение номера телефона"
WRITING_EXPECTATIONS = "Заполнение ожиданий"
WRITING_FOOD_WISHES = "Заполнение особенностей питания"
FINISHED = "Регистрация закончена"

ABOUT_TREAP = "O выезде"
WHAT_TO_TAKE = "Что взять?"
CHANGE_DATA = "Изменить данные"

CALLBACK_WRITING_FIRST_NAME = WRITING_LAST_NAME
CALLBACK_WRITING_LAST_NAME = WRITING_PATRONYMIC
CALLBACK_WRITING_PATRONYMIC = WRITING_GROUP
CALLBACK_WRITING_GROUP = WRITING_PHONE_NUMBER
CALLBACK_WRITING_PHONE_NUMBER = WRITING_EXPECTATIONS
CALLBACK_WRITING_EXPECTATIONS = WRITING_FOOD_WISHES
CALLBACK_WRITING_FOOD_WISHES = FINISHED
CALLBACK_FINISHED = FINISHED

ABOUT_TREAP_CALLBACK = FINISHED
WHAT_TO_TAKE_CALLBACK = FINISHED
CHANGE_DATA_CALLBACK = FINISHED

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_text = "Привет! Я бот для регистрации на Пионерский выезд 2024!"
    if context.user_data:
        reply_text += (
            f" Мы уже знакомы, я кое-что о тебе знаю: {', '.join(context.user_data.keys())}. Давай продолжим общение."
        )
        await update.message.reply_text(reply_text)
        return context.user_data["current_state"]
    else:
        reply_text += (
            " Давай знакомиться))))))))\nНапиши, пожалуйста, своё имя:"
        )
        await update.message.reply_text(reply_text)
        context.user_data["current_state"] = WRITING_FIRST_NAME
        return context.user_data["current_state"]

async def writing_first_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["first_name"] = text
    await update.message.reply_text(f"Отлично, {text}, а теперь введи свою фамилию:")
    return CALLBACK_WRITING_FIRST_NAME

async def writing_last_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["last_name"] = text
    await update.message.reply_text("А теперь введи своё отчество:")
    return CALLBACK_WRITING_LAST_NAME

async def writing_patronymic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["patronymic"] = text
    await update.message.reply_text("А теперь введи свою группу:")
    return CALLBACK_WRITING_PATRONYMIC

ask_phone_number = KeyboardButton(text="Поделиться номером из telegram", request_contact=True)
markup_ask_phone_number = ReplyKeyboardMarkup([[ ask_phone_number ]], one_time_keyboard=True)

async def writing_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["group"] = text
    await update.message.reply_text("Осталось совсем немного, теперь мне нужен твой номер телефона", reply_markup=markup_ask_phone_number)
    return CALLBACK_WRITING_GROUP

async def writing_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["phone_number"] = text
    await update.message.reply_text("Что ты ожидаешь от выезда?")
    return CALLBACK_WRITING_PHONE_NUMBER

answer_no = [["Нет"]]
markup_answer_no = ReplyKeyboardMarkup(answer_no, one_time_keyboard=True)

async def writing_expectations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["expectations"] = text
    await update.message.reply_text("Есть ли у тебя алергия на еду?", markup_answer_no)
    return CALLBACK_WRITING_EXPECTATIONS

async def writing_food_wishes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    context.user_data["food_wishes"] = text
    await update.message.reply_text("Поздравляю! Теперь ты зарегистрирован(а) на Пионерский выезд!")
    return CALLBACK_WRITING_FOOD_WISHES

ABOUT_TREAP = "O выезде"
WHAT_TO_TAKE = "Что взять?"
CHANGE_DATA = "Изменить данные"

reply_keyboard = [
    [ABOUT_TREAP, WHAT_TO_TAKE],
    [CHANGE_DATA]
]
markup_reply_keyboard = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)

async def finished(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Таакс... Мы уже знакомы, вот, что могу предложить", reply_markup=markup_reply_keyboard)
    return CALLBACK_FINISHED

async def about_treap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Пионерский выезд - один из лучших выездов что проходят с сентября по конец августа и с начала мая по конец мая!)")
    return ABOUT_TREAP_CALLBACK

async def what_to_take(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Трусы и куртку!")
    return WHAT_TO_TAKE_CALLBACK

change_data_keyboard = [
    ["Изменить имя", "Изменить фамилию"],
    ["Изменить отчество", "Изменить группу"],
    ["Изменить номер телефона", "Изменить ожидания"],
    ["Изменить особенности питания"]
]
markup_change_data = ReplyKeyboardMarkup(change_data_keyboard, one_time_keyboard=True)

async def change_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Что хочешь поменять? (пока не работает)", reply_markup=markup_change_data)
    return CALLBACK_FINISHED

async def fill_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Допустим, записал, но пока нет, ещё перекину типо ты зарегался")
    return CALLBACK_FINISHED

def facts_to_str(user_data: Dict[str, str]) -> str:
    """Helper function for formatting the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

async def show_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Display the gathered info."""
    await update.message.reply_text(
        f"This is what you already told me: {facts_to_str(context.user_data)}"
    )

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return FINISHED


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    persistence = PicklePersistence(filepath="conversationbot")
    application = Application.builder().token(BOT_TOKEN).persistence(persistence).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WRITING_FIRST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_first_name)
            ],
            WRITING_LAST_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_last_name)
            ],
            WRITING_PATRONYMIC: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_patronymic)
            ],
            WRITING_GROUP: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_group)
            ],
            WRITING_PHONE_NUMBER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_phone_number)
            ],
            WRITING_EXPECTATIONS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_expectations)
            ],
            WRITING_FOOD_WISHES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, writing_food_wishes)
            ],
            FINISHED: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, finished)
            ],
            ABOUT_TREAP: [
                MessageHandler(filters.Regex(f"^{ABOUT_TREAP}$"), about_treap)
            ],
            WHAT_TO_TAKE: [
                MessageHandler(filters.Regex(f"^{WHAT_TO_TAKE}$"), what_to_take)
            ],
            CHANGE_DATA: [
                MessageHandler(filters.Regex(f"^{CHANGE_DATA}$"), change_data)
            ]
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        name="my_conversation",
        persistent=True
    )
    MessageHandler(filters.CONTACT & ~filters.COMMAND, fill_phone_number)

    application.add_handler(conv_handler)

    show_data_handler = CommandHandler("show_data", show_data)
    application.add_handler(show_data_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()