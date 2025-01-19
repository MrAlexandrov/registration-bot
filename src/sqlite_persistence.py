import sqlite3

from telegram.ext import (
    BasePersistence,
    PersistenceInput
)
from typing import DefaultDict, Any, Optional, Dict
from collections import defaultdict
from telegram.ext._utils.types import CD, UD

from logger import logger

class SqlitePersistence(BasePersistence):
    def __init__(self, name: str = 'demo.db'):
        super().__init__(update_interval=1)
        self.store_data = PersistenceInput(bot_data=False, user_data=False, callback_data=False)
        self.db_name = name  # Сохраняем имя базы данных

        # Создаём таблицу, если её нет
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    chat_id INTEGER NOT NULL,
                    message_ts INTEGER NOT NULL,
                    message TEXT NOT NULL
                )
            ''')
            conn.commit()

    def _execute(self, query: str, params: tuple = ()):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            return None

    async def get_chat_data(self) -> DefaultDict[int, Any]:
        chat_data = defaultdict(lambda: {'messages': []})
        rows = self._execute('SELECT * FROM chat_data').fetchall()
        for row in rows:
            chat_id = row[1]
            chat_data[chat_id]['messages'].append(dict(zip(['id', 'chat_id', 'message_ts', 'message'], row)))
        return chat_data

    async def update_chat_data(self, chat_id: int, data: CD) -> None:
        for row in data.get('messages', []):
            existing_row = self._execute('SELECT * FROM chat_data WHERE chat_id = ? AND message_ts = ?',
                                        (chat_id, row['message_ts'])).fetchone()
            if existing_row is None:
                self._execute('INSERT INTO chat_data (chat_id, message_ts, message) VALUES (?, ?, ?)',
                            (chat_id, row['message_ts'], row['message']))
            else:
                self._execute('UPDATE chat_data SET message = ? WHERE chat_id = ? AND message_ts = ?',
                            (row['message'], chat_id, row['message_ts']))

    async def refresh_chat_data(self, chat_id: int, chat_data: Any) -> None:
        data = self._execute('''SELECT * FROM chat_data WHERE chat_id = ?''', (chat_id, ))
        chat_data['messages'] = [dict(zip(['id', 'chat_id', 'message_ts', 'message'], x)) for x in data]

    async def drop_chat_data(self, chat_id: int) -> None:
        self._execute('DELETE FROM chat_data WHERE chat_id = ?', (chat_id,))

    async def get_bot_data(self) -> Any:
        pass

    def update_bot_data(self, data) -> None:
        pass

    def refresh_bot_data(self, bot_data) -> None:
        pass

    def get_user_data(self) -> DefaultDict[int, Any]:
        pass

    def update_user_data(self, user_id: int, data: Any) -> None:
        pass

    def refresh_user_data(self, user_id: int, user_data: Any) -> None:
        pass

    def get_callback_data(self) -> Optional[Any]:
        pass

    def update_callback_data(self, data: Any) -> None:
        pass

    def get_conversations(self, name: str) -> Any:
        pass

    def update_conversation(self, name: str, key, new_state: Optional[object]) -> None:
        pass

    def flush(self) -> None:
        """Метод для очистки базы данных перед завершением работы."""
        self._execute('DELETE FROM chat_data')

    async def drop_user_data(self, user_id: int) -> None:
        pass

    async def get_user_data(self) -> Dict[int, UD]:
        pass