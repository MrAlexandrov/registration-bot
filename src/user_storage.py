import sqlite3
from settings import FIELDS

class UserStorage:
    def __init__(self, db_path="database.sqlite"):
        self.connection = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self._create_table()

    def _create_table(self):
        """Создаёт таблицу на основе FIELDS."""
        fields_sql = ", ".join([f"{field['name']} {field.get('type', 'TEXT')}" for field in FIELDS])
        sql_query = f"""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE,
            state TEXT,
            {fields_sql}
        )
        """
        self.cursor.execute(sql_query)
        self.connection.commit()

    def create_user(self, user_id, initial_state="name"):
        """Создаёт нового пользователя с пустыми полями."""
        columns = ", ".join(["telegram_id", "state"] + [field["name"] for field in FIELDS])
        placeholders = ", ".join(["?"] * (len(FIELDS) + 2))
        self.cursor.execute(
            f"INSERT INTO users ({columns}) VALUES ({placeholders})",
            [user_id, initial_state] + [None] * len(FIELDS),
        )
        self.connection.commit()

    def update_user(self, user_id, field, value):
        """Обновляет одно поле пользователя."""
        self.cursor.execute(f"UPDATE users SET {field} = ? WHERE telegram_id = ?", (value, user_id))
        self.connection.commit()

    def update_state(self, user_id, state):
        """Обновляет состояние пользователя."""
        self.cursor.execute("UPDATE users SET state = ? WHERE telegram_id = ?", (state, user_id))
        self.connection.commit()

    def get_user(self, user_id):
        """Получает данные пользователя по Telegram ID."""
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if not row:
            return None

        # Генерируем словарь на основе FIELDS
        column_names = ["id", "telegram_id", "state"] + [field["name"] for field in FIELDS]
        return dict(zip(column_names, row))

user_storage = UserStorage()
