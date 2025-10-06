import os
import sqlite3
import time

import pandas as pd


def get_actual_table():
    db_path = "./database.sqlite"
    conn = sqlite3.connect(db_path)

    query = "SELECT * FROM users"
    df = pd.read_sql(query, conn)

    conn.close()

    excel_dir = "excel"
    os.makedirs(excel_dir, exist_ok=True)

    file_name = f"database_{time.clock_gettime(0)}.xlsx"
    file_path = os.path.join(excel_dir, file_name)

    df.to_excel(file_path, index=False)

    print("✅ Данные экспортированы")
    return file_path
