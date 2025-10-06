import os
import sqlite3
from datetime import datetime

import pandas as pd


def get_actual_table():
    db_path = "./database.sqlite"
    conn = sqlite3.connect(db_path)

    query = "SELECT * FROM users"
    df = pd.read_sql(query, conn)

    conn.close()

    excel_dir = "excel"
    os.makedirs(excel_dir, exist_ok=True)

    # Используем datetime для генерации уникального имени файла
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"database_{timestamp}.xlsx"
    file_path = os.path.join(excel_dir, file_name)

    df.to_excel(file_path, index=False)

    print("✅ Данные экспортированы")
    return file_path
