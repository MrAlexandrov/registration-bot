import sqlite3
from settings import FIELDS
from constants import NAME, TYPE, STATE

class UserStorage:
    def __init__(self, db_path="database.sqlite"):
        self.db_path = db_path
        self._create_table()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_table(self):
        """Создаёт таблицу на основе FIELDS."""
        fields_sql = ", ".join([f"{field[STATE]} {field.get(TYPE, 'TEXT')}" for field in FIELDS])
        sql_query = f"""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            state TEXT,
            {fields_sql}
        )
        """
        with self._get_connection() as conn:
            conn.execute(sql_query)
            conn.commit()

    def create_user(self, user_id, initial_state=NAME):
        """Создаёт нового пользователя с пустыми полями."""
        columns = ", ".join(["telegram_id", STATE] + [field[STATE] for field in FIELDS])
        placeholders = ", ".join(["?"] * (len(FIELDS) + 2))
        sql = f"INSERT INTO users ({columns}) VALUES ({placeholders})"
        values = [user_id, initial_state] + [None] * len(FIELDS)
        with self._get_connection() as conn:
            conn.execute(sql, values)
            conn.commit()

    def update_user(self, user_id, field, value):
        """Обновляет одно поле пользователя."""
        sql = f"UPDATE users SET {field} = ? WHERE telegram_id = ?"
        with self._get_connection() as conn:
            conn.execute(sql, (value, user_id))
            conn.commit()

    def update_state(self, user_id, state):
        """Обновляет состояние пользователя."""
        sql = "UPDATE users SET state = ? WHERE telegram_id = ?"
        with self._get_connection() as conn:
            conn.execute(sql, (state, user_id))
            conn.commit()

    def get_user(self, user_id):
        """Получает данные пользователя по Telegram ID."""
        sql = "SELECT * FROM users WHERE telegram_id = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id,))
            row = cursor.fetchone()
            if not row:
                return None
            column_names = ["id", "telegram_id", STATE] + [field[STATE] for field in FIELDS]
            return dict(zip(column_names, row))

    def get_all_users(self):
        """Возвращает список всех telegram_id пользователей."""
        sql = "SELECT telegram_id from users"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [row[0] for row in rows]

    def find_users_by_name(self, name_query):
        """Ищет пользователей по части ФИО."""
        sql = "SELECT telegram_id FROM users WHERE name LIKE ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (f"%{name_query}%",))
            rows = cursor.fetchall()
            return [row[0] for row in rows]

user_storage = UserStorage()
