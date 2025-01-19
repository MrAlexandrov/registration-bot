import os
import csv
from spreadsheets import GoogleSpreadsheetClient
from user import User
from settings import FIELDNAMES
import sqlite3
from typing import List
from logger import logger


class UserStorage:
    """Абстрактный интерфейс для хранения данных пользователей."""
    def save_user(self, user):
        raise NotImplementedError

    def get_all_users(self):
        raise NotImplementedError

class CSVFileStorage(UserStorage):
    """Класс для хранения данных пользователей в CSV-файле."""
    
    def __init__(self, file_name="users.csv", fieldnames=FIELDNAMES):
        """
        :param file_name: Имя CSV-файла.
        :param fieldnames: Список полей (столбцов), которые будут использоваться в файле.
        """
        self.file_name = file_name
        self.fieldnames = fieldnames
        
        # Проверяем, существует ли файл
        if not os.path.exists(self.file_name):
            # Создаем файл, если его нет, и добавляем заголовки
            with open(self.file_name, 'w', newline='', encoding='utf-8') as current_file:
                writer = csv.DictWriter(current_file, fieldnames=self.fieldnames)
                writer.writeheader()

    def save_user(self, user):
        """Сохранение объекта пользователя в CSV-файл."""
        with open(self.file_name, 'a', newline='', encoding='utf-8') as current_file:
            writer = csv.DictWriter(current_file, fieldnames=self.fieldnames)
            writer.writerow(user.to_dict())

    def get_all_users(self):
        """Чтение всех зарегистрированных пользователей из CSV-файла."""
        users = []
        with open(self.file_name, 'r', newline='', encoding='utf-8') as current_file:
            reader = csv.DictReader(current_file)
            for row in reader:
                user = User.from_dict(row)
                users.append(user)
        return users


class SQLiteStorage:
    def __init__(self, db_path="users.db"):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        # Исключаем 'user_id' из FIELDNAMES, так как он уже объявлен отдельно
        columns = ", ".join([f"{field} TEXT" for field in FIELDNAMES if field != "user_id"])
        with self.connection as conn:
            conn.execute(f"""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    {columns}
                )
            """)

    def save_user(self, user: User):
        placeholders = ", ".join(["?"] * len(FIELDNAMES))
        fields = ", ".join(FIELDNAMES)
        values = [getattr(user, field) for field in FIELDNAMES]
        values.insert(0, user.user_id)  # Добавляем user_id как первый параметр
        with self.connection as conn:
            conn.execute(f"""
                INSERT INTO users (user_id, {fields})
                VALUES ({placeholders}, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                {', '.join([f'{field} = EXCLUDED.{field}' for field in FIELDNAMES])}
            """, values)

    def get_user(self, user_id: int) -> User:
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if row:
            data = {FIELDNAMES[i]: row[i] for i in range(len(FIELDNAMES))}
            return User(
                user_id=data.get("user_id"),
                timestamp=data.get("timestamp"),
                username=data.get("username"),
                full_name=data.get("full_name", ""),
                birth_date=data.get("birth_date", ""),
                study_group=data.get("study_group", ""),
                phone_number=data.get("phone_number", ""),
                expectations=data.get("expectations", ""),
                food_wishes=data.get("food_wishes", "")
            )
        return None

    def get_all_users(self) -> List[User]:
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        users = []
        for row in rows:
            data = {FIELDNAMES[i]: row[i] for i in range(len(FIELDNAMES))}
            users.append(User(
                user_id=data.get("user_id"),
                timestamp=data.get("timestamp"),
                username=data.get("username"),
                full_name=data.get("full_name", ""),
                birth_date=data.get("birth_date", ""),
                study_group=data.get("study_group", ""),
                phone_number=data.get("phone_number", ""),
                expectations=data.get("expectations", ""),
                food_wishes=data.get("food_wishes", "")
            ))
        return users

    def close(self):
        self.connection.close()


class CombinedStorage(UserStorage):
    """Класс для хранения данных как в CSV-файле, так и в Google таблице."""

    def __init__(self, csv_file_name, fieldnames=FIELDNAMES, debug_mode=False, use_sqlite=False, sqlite_db_path="users.db"):
        """
        Инициализация хранилищ данных
        
        :param csv_file_name: Имя файла CSV.
        :param credentials_file: Путь к файлу с учетными данными для Google API.
        :param spreadsheet_id: ID Google таблицы.
        :param fieldnames: Список полей (столбцов).
        :param sheet_id: ID листа Google таблицы.
        :param sheet_title: Название листа Google таблицы.
        :param debug_mode: Флаг включения режима отладки.
        """
        self.csv_storage = CSVFileStorage(file_name=csv_file_name, fieldnames=fieldnames)

        if use_sqlite:
            self.sqlite_storage = SQLiteStorage(db_path=sqlite_db_path)
        else:
            self.sqlite_storage = None

    def save_user(self, user):
        self.csv_storage.save_user(user)
        if self.sqlite_storage:
            self.sqlite_storage.save_user(user)

    def get_all_users(self):
        csv_users = self.csv_storage.get_all_users()
        if self.sqlite_storage:
            users_sqlite = self.sqlite_storage.get_all_users()
            return users_sqlite
        return csv_users

    def get_user(self, user_id: int):
        if self.sqlite_storage:
            return self.sqlite_storage.get_user(user_id)
        return None

    def close(self):
        if self.sqlite_storage:
            self.sqlite_storage.close()

from settings import FIELDNAMES

# TODO: Сделать различные хранилища опциональными
storage = CombinedStorage(
    csv_file_name="users.csv",
    fieldnames=FIELDNAMES,
    debug_mode=False,
    use_sqlite=True,  # Включаем SQLite
    sqlite_db_path="users.db"  # Путь к SQLite базе данных
)
