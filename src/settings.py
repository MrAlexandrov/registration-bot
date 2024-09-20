from os import getenv
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменной окружения
BOT_TOKEN = getenv('BOT_TOKEN')
SPREADSHEET_ID = getenv('SPREADSHEET_ID')
GOOGLE_CREDENTIALS_FILE = getenv('GOOGLE_CREDENTIALS_FILE')

FIELDNAMES = ["user_id", "first_name", "last_name", "group", "username"]
# USER_ID='user_id'
# FIRST_NAME='first_name'
# LAST_NAME='last_name'
# GROUP='group'
# NICKNAME='NICKNAME'

if BOT_TOKEN is None:
    raise ValueError("Токен не найден! Убедитесь, что файл .env правильно настроен.")

if SPREADSHEET_ID is None:
    raise ValueError("SPREADSHEET_ID не установлен")

if GOOGLE_CREDENTIALS_FILE is None:
    raise ValueError("GOOGLE_CREDENTIALS_FILE не найден")