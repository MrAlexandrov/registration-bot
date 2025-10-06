import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def get_actual_table(db_path: str = "data/database.sqlite") -> str:
    """
    Экспортирует данные из базы данных в Excel файл.

    Args:
        db_path: Путь к файлу базы данных SQLite

    Returns:
        str: Путь к созданному Excel файлу

    Raises:
        FileNotFoundError: Если файл базы данных не найден
        sqlite3.Error: При ошибке работы с базой данных
        Exception: При других ошибках экспорта
    """
    try:
        # Проверяем существование файла БД
        if not os.path.exists(db_path):
            error_msg = f"Файл базы данных не найден: {db_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        logger.info(f"Подключение к БД: {db_path}")

        try:
            # Читаем данные
            query = "SELECT * FROM users"
            df = pd.read_sql(query, conn)
            logger.info(f"Прочитано {len(df)} записей из БД")

        finally:
            conn.close()

        # Создаём директорию для экспорта
        excel_dir = Path("excel")
        excel_dir.mkdir(exist_ok=True)

        # Генерируем имя файла с временной меткой
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"database_{timestamp}.xlsx"
        file_path = excel_dir / file_name

        # Экспортируем в Excel
        df.to_excel(file_path, index=False)
        logger.info(f"✅ Данные экспортированы в {file_path}")
        print(f"✅ Данные экспортированы в {file_path}")

        return str(file_path)

    except FileNotFoundError:
        raise
    except sqlite3.Error as e:
        error_msg = f"Ошибка работы с базой данных: {e}"
        logger.error(error_msg)
        raise sqlite3.Error(error_msg) from e
    except Exception as e:
        error_msg = f"Ошибка при экспорте данных: {e}"
        logger.error(error_msg)
        raise Exception(error_msg) from e
