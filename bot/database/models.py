# bot/database/models.py

from dataclasses import dataclass

@dataclass
class User:
    telegram_nick: str
    full_name: str
    group: str
    birth_date: str  # Можно использовать datetime.date для более строгой типизации
