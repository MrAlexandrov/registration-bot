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

FIELDS = [
    {"name": "name", "type": "TEXT", "question": "Как вас зовут?", "validator": validate_name},
    {"name": "phone", "type": "TEXT", "question": "Введите ваш номер телефона:", "validator": validate_phone},
    {"name": "email", "type": "TEXT", "question": "Введите ваш email:", "validator": validate_email},
    {"name": "age", "type": "INTEGER", "question": "Введите ваш возраст:", "validator": validate_age},
]
