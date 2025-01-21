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

from validators import validate_name, validate_phone, validate_email, validate_age, validate_date
from formatters import format_phone, format_date

FIELDS = [
    {
        "name": "name",
        "label": "Имя",
        "message": "Давай знакомиться, напиши ФИО",
        "validator": validate_name,
        "formatter": None,
        "type": "TEXT",
    },
    {
        "name": "phone",
        "label": "Телефон",
        "message": "А теперь напиши номер телефона, или поделись им из Telegram",
        "validator": validate_phone,
        "formatter": format_phone,
        "type": "TEXT",
        "request_contact": True
    },
    {
        "name": "email",
        "label": "Email",
        "message": "Теперь напиши свою email-почту",
        "validator": validate_email,
        "formatter": None,
        "type": "TEXT",
    },
    {
        "name": "birth_date",
        "label": "Дата рождения",
        "message": "А когда у тебя день рождения?",
        "validator": validate_date,
        "formatter": format_date,
        "type": "TEXT",
    },
]

def generate_registration_message():
    """Генерирует строку сообщения для состояния 'registered' на основе FIELDS."""
    message = "Отлично! Вот, что я запомнил:\n"
    
    # Для каждого поля из FIELDS добавляем в сообщение строку с placeholder'ом без пробелов
    for field in FIELDS:
        label = field["label"]
        message += f"{label}: `{{{{field['name']}}}}`\n"  # Убираем пробелы вокруг {field['name']}
    
    return message

POST_REGISTRATION_STATES = [
    {
        "name" : "registered",
        "message" : generate_registration_message(),
        "buttons": ["Изменить данные"],  # Здесь можно добавить любые действия
    },
    {
        "name" : "edit",
        "message": "Что хочешь изменить?",
        "buttons": lambda: [field["label"] for field in FIELDS] + ["Отмена"],   
    },
    {
        "name" : "edit_name",
        "message": "Введи новое ФИО",
        "next_state": "registered",
    },
    {
        "name" : "edit_phone",
        "message": "Введи новый номер телефона",
        "next_state": "registered",
        "request_contact": True,
    },
    {
        "name" : "edit_email",
        "message": "Введи новый email",
        "next_state": "registered",
    },
    {
        "name" : "edit_birth_date",
        "message": "Введи новую дату рождения",
        "next_state": "registered",
    },
]
