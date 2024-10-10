from os import getenv
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменной окружения
# BOT_TOKEN = getenv('TEST_BOT_TOKEN')
# SPREADSHEET_ID = getenv('TEST_SPREADSHEET_ID')
# GOOGLE_CREDENTIALS_FILE = getenv('TEST_GOOGLE_CREDENTIALS_FILE')

BOT_TOKEN = getenv('RELEASE_BOT_TOKEN')
SPREADSHEET_ID = getenv('RELEASE_SPREADSHEET_ID')
GOOGLE_CREDENTIALS_FILE = getenv('RELEASE_GOOGLE_CREDENTIALS_FILE')
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

if SPREADSHEET_ID is None:
    raise ValueError("SPREADSHEET_ID не установлен")

if GOOGLE_CREDENTIALS_FILE is None:
    raise ValueError("GOOGLE_CREDENTIALS_FILE не найден")

if ROOT_ID is None:
    raise ValueError("ROOT_ID не найден")

ADMIN_IDS = []

AGREED_USERS = []

CANT_RIDE_USERS = []

CANT_RIDE_MISSED_USERS = []