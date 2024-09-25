from os import getenv
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменной окружения
BOT_TOKEN = getenv('BOT_TOKEN')
SPREADSHEET_ID = getenv('SPREADSHEET_ID')
GOOGLE_CREDENTIALS_FILE = getenv('GOOGLE_CREDENTIALS_FILE')
ROOT_ID = getenv('ADMIN_ID')

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

ADMIN_IDS = []
ADMIN_IDS.append(int(ROOT_ID))

if BOT_TOKEN is None:
    raise ValueError("Токен не найден! Убедитесь, что файл .env правильно настроен.")

if SPREADSHEET_ID is None:
    raise ValueError("SPREADSHEET_ID не установлен")

if GOOGLE_CREDENTIALS_FILE is None:
    raise ValueError("GOOGLE_CREDENTIALS_FILE не найден")