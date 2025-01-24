import sqlite3
import pandas as pd
import time
import os

def get_actual_table():
    db_path = "./database.sqlite"
    conn = sqlite3.connect(db_path)

    query = "SELECT * FROM users"
    df = pd.read_sql(query, conn)

    conn.close()

    file_name = f"database_{time.clock_gettime(0)}.xlsx"

    df.to_excel(file_name, index=False)

    new_file_name = f"./excel/{file_name}"

    os.replace(file_name, new_file_name)

    print("✅ Данные экспортированы")
    return new_file_name
