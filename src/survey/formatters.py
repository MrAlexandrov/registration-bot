"""
Форматтеры для полей опроса.
Следует принципу Single Responsibility - каждый форматтер отвечает за одну задачу.
"""

import re
from abc import ABC, abstractmethod


class Formatter(ABC):
    """Базовый класс для всех форматтеров."""

    @abstractmethod
    def format(self, value: str) -> str:
        """Форматирует значение."""
        pass


class TextFormatter(Formatter):
    """Базовый форматтер для текста."""

    def format(self, value: str) -> str:
        return value.strip() if value else ""


class PhoneDbFormatter(Formatter):
    """Форматтер телефона для сохранения в БД."""

    def format(self, value: str) -> str:
        # Удаляем все символы кроме цифр
        phone = re.sub(r"\D", "", str(value))

        # Заменяем 8 на 7 в начале
        if phone.startswith("8"):
            phone = "7" + phone[1:]

        return phone


class PhoneDisplayFormatter(Formatter):
    """Форматтер телефона для отображения пользователю."""

    def format(self, value: str) -> str:
        if not value:
            return "Не указан"

        # Сначала форматируем для БД, затем добавляем +
        db_formatter = PhoneDbFormatter()
        phone = db_formatter.format(value)
        return "+" + phone


class DateDbFormatter(Formatter):
    """Форматтер даты для сохранения в БД."""

    def format(self, value: str) -> str:
        if not value:
            return ""

        # Разбиваем дату на день, месяц и год
        day, month, year = value.split(".")

        # Добавляем ведущие нули
        day = day.zfill(2)
        month = month.zfill(2)

        return f"{day}.{month}.{year}"


class UsernameDbFormatter(Formatter):
    """Форматтер username для сохранения в БД."""

    def format(self, value: str) -> str:
        return value.strip() if value else None


class UsernameDisplayFormatter(Formatter):
    """Форматтер username для отображения."""

    def format(self, value: str) -> str:
        if not value:
            return "Не указан"
        return f"@{value}"


class DefaultDisplayFormatter(Formatter):
    """Форматтер по умолчанию для отображения."""

    def format(self, value: str) -> str:
        return value if value else "Не указано"


# Фабрика форматтеров
class FormatterFactory:
    """Фабрика для создания форматтеров."""

    @staticmethod
    def create_text() -> TextFormatter:
        return TextFormatter()

    @staticmethod
    def create_phone_db() -> PhoneDbFormatter:
        return PhoneDbFormatter()

    @staticmethod
    def create_phone_display() -> PhoneDisplayFormatter:
        return PhoneDisplayFormatter()

    @staticmethod
    def create_date_db() -> DateDbFormatter:
        return DateDbFormatter()

    @staticmethod
    def create_username_db() -> UsernameDbFormatter:
        return UsernameDbFormatter()

    @staticmethod
    def create_username_display() -> UsernameDisplayFormatter:
        return UsernameDisplayFormatter()

    @staticmethod
    def create_default_display() -> DefaultDisplayFormatter:
        return DefaultDisplayFormatter()


# Функции-обертки для обратной совместимости
def format_text_db(value: str) -> str:
    return FormatterFactory.create_text().format(value)


def format_phone_db(value: str) -> str:
    return FormatterFactory.create_phone_db().format(value)


def format_phone_display(value: str) -> str:
    return FormatterFactory.create_phone_display().format(value)


def format_date_db(value: str) -> str:
    return FormatterFactory.create_date_db().format(value)


def format_username_db(value: str) -> str:
    return FormatterFactory.create_username_db().format(value)


def format_username_display(value: str) -> str:
    return FormatterFactory.create_username_display().format(value)


def format_default_display(value: str) -> str:
    return FormatterFactory.create_default_display().format(value)
