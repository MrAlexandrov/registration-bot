from os import getenv
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменной окружения
BOT_TOKEN = getenv('TEST_BOT_TOKEN')

# BOT_TOKEN = getenv('RELEASE_BOT_TOKEN')
ROOT_ID = int(getenv('ROOT_ID'))

FIELDNAMES = [
    "user_id", 
    "timestamp", 
    "username", 
    "full_name",
    "birth_date",
    "study_group", 
    "phone_number", 
    "expectations", 
    "food_wishes"
]

if BOT_TOKEN is None:
    raise ValueError("Токен не найден! Убедитесь, что файл .env правильно настроен.")

if ROOT_ID is None:
    raise ValueError("ROOT_ID не найден")

ADMIN_IDS = []

from validators import (
    validate_phone,
    validate_email,
    validate_date,
    validate_probability,
)
from formatters import (
    format_phone_db,
    format_phone_display,

    format_date,

    format_probability_display,
)

FIELDS = [
    {
        "name":                 "name",
        "label":                "Имя",
        "message":              "Давай знакомиться, напиши ФИО",
        "validator":            None,
        "db_formatter":         None,                               # Для БД
        "display_formatter":    None,                               # Для вывода
        "formatter":            None,
        "type":                 "TEXT",
    },
    {
        "name":                 "phone",
        "label":                "Телефон",
        "message":              "А теперь напиши номер телефона, или поделись им из Telegram",
        "validator":            validate_phone,
        "db_formatter":         format_phone_db,
        "display_formatter":    format_phone_display,
        "type":                 "TEXT",
        "request_contact":      True
    },
    {
        "name":                 "email",
        "label":                "Email",
        "message":              "Теперь напиши свою email-почту",
        "validator":            validate_email,
        "db_formatter":         None,
        "display_formatter":    None,
        "type":                 "TEXT",
    },
    {
        "name":                 "birth_date",
        "label":                "Дата рождения",
        "message":              "А когда у тебя день рождения?",
        "validator":            validate_date,
        "db_formatter":         format_date,
        "display_formatter":    None,
        "type": "TEXT",
    },
    {
        "name":                 "probability_first",
        "label":                "Вероятность поехать на первую смену",
        "message":              "Напиши, с какой вероятностью ты сможешь поехать на первую смену?",
        "validator":            validate_probability,
        "db_formatter":         None,
        "display_formatter":    format_probability_display,
        "type":                 "TEXT",
    },
    {
        "name":                 "probability_second",
        "label":                "Вероятность поехать на вторую смену",
        "message":              "С какой вероятностью ты сможешь поехать на вторую смену?",
        "validator":            validate_probability,
        "db_formatter":         None,
        "display_formatter":    format_probability_display,
        "type":                 "TEXT",
    },
]

def generate_registered_message():
    """Генерирует сообщение о регистрации на основе FIELDS."""
    message = "Отлично! Вот, что я запомнил:\n"
    for field in FIELDS:
        message += f"{field['label']}: `{{{field['name']}}}`\n"  # <-- правильная подстановка
    return message


POST_REGISTRATION_STATES = [
    {
        "name":                 "registered",
        "message":              generate_registered_message(),
        "buttons":              ["Изменить данные"],  # Здесь можно добавить любые действия
    },
    {
        "name":                 "edit",
        "message":              "Что хочешь изменить?",
        "buttons":              lambda: [field["label"] for field in FIELDS] + ["Отмена"],   
    },
    {
        "name":                 "edit_name",
        "message":              "Введи новое ФИО",
        "next_state":           "registered",
    },
    {
        "name":                 "edit_phone",
        "message":              "Введи новый номер телефона",
        "next_state":           "registered",
        "request_contact":      True,
    },
    {
        "name":                 "edit_email",
        "message":              "Введи новый email",
        "next_state":           "registered",
    },
    {
        "name":                 "edit_birth_date",
        "message":              "Введи новую дату рождения",
        "next_state":           "registered",
    },
    {
        "name":                 "edit_probability_first",
        "message":              "Напиши, с какой вероятностью ты сможешь поехать на первую смену?",
        "next_state":           "registered",
    },
    {
        "name":                 "edit_probability_second",
        "message":              "С какой вероятностью ты сможешь поехать на вторую смену?",
        "next_state":           "registered",  
    },
]
