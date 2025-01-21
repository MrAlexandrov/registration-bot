from telegram.ext import BasePersistence
import sqlite3
from typing import DefaultDict, Dict, Any, Optional
from collections import defaultdict
from settings import FIELDS

USER_FIELDS = {
    field["name"]: field["type"]
    for field in FIELDS
}

class SqliteUserPersistence(BasePersistence):
    """Persistence-класс для хранения данных пользователей и их текущего состояния."""

    def __init__(self, db_name="registration_data.db"):
        super().__init__(update_interval=1)
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._initialize_database()

    def _initialize_database(self):
        """Создаёт таблицу, если её нет, и добавляет новые поля."""
        columns = ["id INTEGER PRIMARY KEY", "telegram_id INTEGER UNIQUE", "state TEXT"]
        columns += [f"{field} {USER_FIELDS[field]}" for field in USER_FIELDS]

        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS users ({', '.join(columns)})")
        self.conn.commit()

    async def get_user_data(self) -> DefaultDict[int, Dict[str, Any]]:
        """Загружает данные пользователей в user_data (используется для восстановления контекста)."""
        self.cursor.execute("SELECT * FROM users")
        rows = self.cursor.fetchall()
        user_data = defaultdict(dict)

        for row in rows:
            user_id = row[1]
            user_data[user_id] = dict(zip(["state"] + list(USER_FIELDS.keys()), row[2:]))

        return user_data

    async def update_user_data(self, user_id: int, data: Dict[str, Any], state: Optional[str] = None) -> None:
        """Сохраняет или обновляет данные пользователя + текущее состояние."""
        existing_users = await self.get_user_data()

        if user_id not in existing_users:
            # ✅ Создаём пользователя, если его ещё нет в базе
            print(f"[DEBUG] Adding new user {user_id} to the database")
            self.cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (user_id,))
            self.conn.commit()

        if not data and state is None:
            print(f"[WARNING] Skipping update for user {user_id} because no data is provided.")
            return  # ❗ Ничего не обновляем, если данных нет

        # ✅ Формируем SQL-запрос для обновления
        update_fields = []
        values = []

        for key, value in data.items():
            if value is not None:  # ❗ Записываем только непустые значения
                update_fields.append(f"{key} = ?")
                values.append(value)

        if state is not None:
            update_fields.append("state = ?")
            values.append(state)

        if not update_fields:
            print(f"[WARNING] No valid fields to update for user {user_id}")
            return

        values.append(user_id)

        sql_query = f"UPDATE users SET {', '.join(update_fields)} WHERE telegram_id = ?"
        print(f"[DEBUG] SQL EXECUTE: {sql_query} | VALUES: {values}")

        self.cursor.execute(sql_query, values)
        self.conn.commit()

    async def get_conversations(self, name: str) -> Dict[int, str]:
        """Возвращает текущее состояние пользователей для ConversationHandler."""
        
        self.cursor.execute("SELECT telegram_id, state FROM users WHERE state IS NOT NULL")
        result = {}
        for row in self.cursor.fetchall():
            telegram_id, state = row[0], row[1]

            # 🚨 Отладка
            print(f"[DEBUG] get_conversations: user_id={telegram_id}, type={type(telegram_id)}, state={state}, type={type(state)}")

            if isinstance(state, str):  
                result[telegram_id] = state
            else:
                result[telegram_id] = str(state) if state is not None else None  

        print(f"[DEBUG] get_conversations: FINAL RESULT = {result}")
        return result

    async def update_conversation(self, name: str, key, new_state: Optional[str]) -> None:
        """Обновляет текущее состояние пользователя."""
        
        print(f"[DEBUG] update_conversation: BEFORE FIX key={key}, type={type(key)}, new_state={new_state}, type={type(new_state)}")

        if isinstance(key, tuple):
            key = key[0]

        print(f"[DEBUG] update_conversation: AFTER FIX key={key}, type={type(key)}")

        if new_state is None:
            self.cursor.execute("UPDATE users SET state = NULL WHERE telegram_id = ?", (key,))
        else:
            new_state_str = str(new_state)
            self.cursor.execute("UPDATE users SET state = ? WHERE telegram_id = ?", (new_state_str, key))

        self.conn.commit()

    async def drop_user_data(self, user_id: int) -> None:
        """Удаляет пользователя из БД."""
        self.cursor.execute("DELETE FROM users WHERE telegram_id = ?", (user_id,))
        self.conn.commit()

    # ✅ Добавляем недостающие методы
    async def get_chat_data(self) -> DefaultDict[int, Any]:
        """Возвращает данные чатов (не используется, но должен быть определён)."""
        return defaultdict(dict)

    async def update_chat_data(self, chat_id: int, data: Any) -> None:
        """Обновляет данные чатов (не используется, но должен быть определён)."""
        pass

    async def drop_chat_data(self, chat_id: int) -> None:
        """Удаляет данные чатов (не используется, но должен быть определён)."""
        pass

    async def get_bot_data(self) -> Dict[str, Any]:
        """Возвращает данные бота (не используется, но должен быть определён)."""
        return {}

    async def update_bot_data(self, data: Dict[str, Any]) -> None:
        """Обновляет данные бота (не используется, но должен быть определён)."""
        pass

    async def get_callback_data(self) -> Optional[Any]:
        """Возвращает callback-данные (не используется, но должен быть определён)."""
        return None

    async def update_callback_data(self, data: Any) -> None:
        """Обновляет callback-данные (не используется, но должен быть определён)."""
        pass

    async def refresh_chat_data(self, chat_id: int, chat_data: Any) -> None:
        """Обновляет кэшированные данные чатов (не используется, но должен быть определён)."""
        pass

    async def refresh_user_data(self, user_id: int, user_data: Any) -> None:
        """Обновляет кэшированные данные пользователей (не используется, но должен быть определён)."""
        pass

    async def refresh_bot_data(self, bot_data: Any) -> None:
        """Обновляет кэшированные данные бота (не используется, но должен быть определён)."""
        pass

    def flush(self) -> None:
        """Закрывает соединение с базой данных."""
        if hasattr(self, "conn") and self.conn:
            print("[DEBUG] Flushing persistence and closing database connection.")
            self.conn.close()
