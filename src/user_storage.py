import sqlite3
from typing import Dict, Any, Optional

class UserStorage:
    def __init__(self, db_path: str = "database.sqlite"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        """Создаём таблицу пользователей (если нет)."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE,
                state TEXT,
                name TEXT,
                phone TEXT,
                email TEXT,
                age TEXT
            )
        """)
        self.conn.commit()

    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получает данные пользователя по Telegram ID."""
        self.cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (user_id,))
        row = self.cursor.fetchone()

        if row:
            return {
                "id": row[0],
                "telegram_id": row[1],
                "state": row[2],
                "name": row[3],
                "phone": row[4],
                "email": row[5],
                "age": row[6],
            }
        return None

    def create_user(self, user_id: int):
        """Создаёт нового пользователя."""
        self.cursor.execute("INSERT INTO users (telegram_id, state) VALUES (?, ?)", (user_id, "name"))
        self.conn.commit()

    def update_user(self, user_id: int, field: str, value: str):
        """Обновляет одно поле пользователя."""
        self.cursor.execute(f"UPDATE users SET {field} = ? WHERE telegram_id = ?", (value, user_id))
        self.conn.commit()

    def update_state(self, user_id: int, state: str):
        """Обновляет состояние пользователя."""
        self.cursor.execute("UPDATE users SET state = ? WHERE telegram_id = ?", (state, user_id))
        self.conn.commit()
