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

from validators import validate_name, validate_phone, validate_email, validate_age
from formatters import format_phone

FIELDS = [
    {
        "name": "name",
        "label": "Имя",
        "message": "Как вас зовут?",
        "validator": validate_name,
        "formatter": None,
        "type": "TEXT",
    },
    {
        "name": "phone",
        "label": "Телефон",
        "message": "Введите ваш номер телефона:",
        "validator": validate_phone,
        "formatter": format_phone,
        "type": "TEXT",
        "request_contact": True
    },
    {
        "name": "email",
        "label": "Email",
        "message": "Введите ваш email:",
        "validator": validate_email,
        "formatter": None,
        "type": "TEXT",
    },
    {
        "name": "age",
        "label": "Возраст",
        "message": "Введите ваш возраст:",
        "validator": validate_age,
        "formatter": None,
        "type": "INTEGER",
    },
]

POST_REGISTRATION_STATES = [
    {
        "name" : "registered",
        "message" : "Вы успешно зарегистрированы! Выберите действие:",
        "buttons": ["Изменить данные"],  # Здесь можно добавить любые действия
    },
    {
        "name" : "edit",
        "message": "Что вы хотите изменить?",
        "buttons": lambda: [field["label"] for field in FIELDS] + ["Отмена"],   
    },
    {
        "name" : "edit_name",
        "message": "Введите новое имя:",
        "next_state": "registered",
    },
    {
        "name" : "edit_phone",
        "message": "Введите новый номер телефона:",
        "next_state": "registered",
        "request_contact": True,
    },
    {
        "name" : "edit_email",
        "message": "Введите новый email:",
        "next_state": "registered",
    },
    {
        "name" : "edit_age",
        "message": "Введите новый возраст:",
        "next_state": "registered",
    },
]
