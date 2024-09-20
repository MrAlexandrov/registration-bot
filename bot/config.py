# bot/config.py

import os
from dotenv import load_dotenv

load_dotenv()

CONFIG = {
    'storage': {
        'type': os.getenv('STORAGE_TYPE', 'sqlite'),  # 'csv', 'sqlite', 'google_sheets'
        'file_path': os.getenv('CSV_FILE_PATH', 'users.csv'),
        'db_path': os.getenv('SQLITE_DB_PATH', 'users.db'),
        'credentials_file': os.getenv('GOOGLE_CREDENTIALS_FILE', 'credentials.json'),
        'spreadsheet_id': os.getenv('GOOGLE_SPREADSHEET_ID'),
        'sheet_title': os.getenv('GOOGLE_SHEET_TITLE', 'Sheet1'),
        'debug_mode': os.getenv('GOOGLE_DEBUG_MODE', 'False') == 'True'
    },
    'BOT_TOKEN': os.getenv('BOT_TOKEN')
}
