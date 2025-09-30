import sqlite3
import json
from datetime import datetime

class FeedbackStorage:
    def __init__(self, db_path="database.sqlite"):
        self.db_path = db_path
        self._create_tables()

    def _get_connection(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _create_tables(self):
        """Создаёт таблицы для системы обратной связи."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Таблица опросов
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS surveys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            # Таблица вопросов
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                text TEXT NOT NULL,
                question_type TEXT NOT NULL,
                options TEXT,
                FOREIGN KEY (survey_id) REFERENCES surveys (id)
            )
            """)
            # Таблица ответов
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                answer_text TEXT NOT NULL,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES questions (id)
            )
            """)
            # Таблица для отслеживания отправки опросов
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS survey_sends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                survey_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL,
                FOREIGN KEY (survey_id) REFERENCES surveys (id)
            )
            """)
            conn.commit()

    def create_survey(self, name):
        """Создаёт новый опрос и возвращает его ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO surveys (name) VALUES (?)", (name,))
            conn.commit()
            return cursor.lastrowid

    def add_question_to_survey(self, survey_id, text, question_type, options=None):
        """Добавляет вопрос к опросу."""
        options_json = json.dumps(options) if options else None
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO questions (survey_id, text, question_type, options) VALUES (?, ?, ?, ?)",
                (survey_id, text, question_type, options_json)
            )
            conn.commit()

    def save_answer(self, user_id, question_id, answer_text):
        """Сохраняет ответ пользователя."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO answers (user_id, question_id, answer_text) VALUES (?, ?, ?)",
                (user_id, question_id, answer_text)
            )
            conn.commit()

    def log_survey_send(self, survey_id, user_id, status="sent"):
        """Логирует отправку опроса пользователю."""
        with self._get_connection() as conn:
            conn.execute(
                "INSERT INTO survey_sends (survey_id, user_id, status) VALUES (?, ?, ?)",
                (survey_id, user_id, status)
            )
            conn.commit()

    def get_survey_questions(self, survey_id):
        """Получает все вопросы для данного опроса."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, text, question_type, options FROM questions WHERE survey_id = ?", (survey_id,))
            rows = cursor.fetchall()
            questions = []
            for row in rows:
                questions.append({
                    "id": row[0],
                    "text": row[1],
                    "question_type": row[2],
                    "options": json.loads(row[3]) if row[3] else None
                })
            return questions

    def get_question_details(self, question_id):
        """Получает детали вопроса, включая survey_id."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT survey_id FROM questions WHERE id = ?", (question_id,))
            row = cursor.fetchone()
            return {"survey_id": row[0]} if row else None

    def get_user_answers_for_survey(self, user_id, survey_id):
        """Получает ответы пользователя на конкретный опрос."""
        sql = """
        SELECT q.text, a.answer_text
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        WHERE a.user_id = ? AND q.survey_id = ?
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (user_id, survey_id))
            return cursor.fetchall()

    def get_all_surveys(self):
        """Возвращает список всех опросов (id, name)."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM surveys ORDER BY created_at DESC")
            return cursor.fetchall()

    def get_survey_results(self, survey_id):
        """Возвращает все ответы для данного опроса."""
        sql = """
        SELECT q.text, a.answer_text, u.name
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        JOIN users u ON a.user_id = u.telegram_id
        WHERE q.survey_id = ?
        ORDER BY u.name, q.id
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (survey_id,))
            return cursor.fetchall()

    def find_users_by_answer(self, question_id, answer_text):
        """Находит пользователей, давших определённый ответ на вопрос."""
        sql = "SELECT user_id FROM answers WHERE question_id = ? AND answer_text = ?"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, (question_id, answer_text))
            rows = cursor.fetchall()
            return [row[0] for row in rows]

feedback_storage = FeedbackStorage()