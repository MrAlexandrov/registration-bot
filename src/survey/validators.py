"""
Валидаторы для полей опроса.
Следует принципу Single Responsibility - каждый валидатор отвечает за одну задачу.
"""

import re
from abc import ABC, abstractmethod
from collections.abc import Callable


class Validator(ABC):
    """Базовый класс для всех валидаторов."""

    @abstractmethod
    def validate(self, value: str) -> tuple[bool, str | None]:
        """Валидирует значение и возвращает (is_valid, error_message)."""
        pass


class NonEmptyValidator(Validator):
    """Валидатор для проверки непустых значений."""

    def __init__(self, error_message: str = "Поле не может быть пустым."):
        self.error_message = error_message

    def validate(self, value: str) -> tuple[bool, str | None]:
        if not value or len(value.strip()) == 0:
            return False, self.error_message
        return True, None


class PhoneValidator(Validator):
    """Валидатор для номеров телефонов."""

    def __init__(
        self,
        error_message: str = "Неверный формат номера телефона. Пожалуйста, введите номер в формате +7 (XXX) XXX-XX-XX или 8 (XXX) XXX-XX-XX.",
    ):
        self.error_message = error_message

    def validate(self, value: str) -> tuple[bool, str | None]:
        # Удаляем все символы кроме цифр
        phone = re.sub(r"\D", "", str(value))

        # Заменяем 8 на 7 в начале
        if phone.startswith("8"):
            phone = "7" + phone[1:]

        # Проверяем формат
        pattern = r"^(7)\d{10}$"
        if not re.match(pattern, phone):
            return False, self.error_message
        return True, None


class EmailValidator(Validator):
    """Валидатор для email адресов."""

    def __init__(self, error_message: str = "Неверный формат email. Пожалуйста, введите корректный email."):
        self.error_message = error_message

    def validate(self, value: str) -> tuple[bool, str | None]:
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", value):
            return False, self.error_message
        return True, None


class GroupValidator(Validator):
    """Валидатор для групп."""

    def __init__(self, error_message: str = "Неверный формат группы. Пожалуйста, введите корректную группу."):
        self.error_message = error_message
        self.pattern = r"^[а-яА-Я]{1,5}\d{0,2}[сицСИЦ]?-([1-9]|1[0-6])[1-9]([абмтАБМТ]?[вВ]?)$"

    def validate(self, value: str) -> tuple[bool, str | None]:
        if not re.match(self.pattern, value):
            return False, self.error_message
        return True, None


class DateValidator(Validator):
    """Валидатор для дат в формате ДД.ММ.ГГГГ."""

    def __init__(self, error_message: str = "Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ."):
        self.error_message = error_message

    def validate(self, value: str) -> tuple[bool, str | None]:
        pattern = r"^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\.(\d{4})$"
        match = re.match(pattern, value)
        if not match:
            return False, self.error_message

        year = int(match.group(3))
        if year < 1980 or year > 2009:
            return (
                False,
                "Немного не верится, что ты родился в этом году. Но могу ошибаться, если так, введи, пожалуйста, 2000 год, потом разберёмся.",
            )

        return True, None


class OptionsValidator(Validator):
    """Валидатор для выбора из списка опций."""

    def __init__(self, options: list[str], error_message: str = "Пожалуйста, выберите один из предложенных вариантов."):
        self.options = options
        self.error_message = error_message

    def validate(self, value: str) -> tuple[bool, str | None]:
        if value not in self.options:
            return False, self.error_message
        return True, None


class YesNoValidator(OptionsValidator):
    """Валидатор для ответов Да/Нет."""

    def __init__(self, error_message: str = "Пожалуйста, выберите 'Да' или 'Нет'."):
        super().__init__(["Да", "Нет"], error_message)


# Фабрика валидаторов для удобства использования
class ValidatorFactory:
    """Фабрика для создания валидаторов."""

    @staticmethod
    def create_non_empty(error_message: str | None = None) -> NonEmptyValidator:
        if error_message:
            return NonEmptyValidator(error_message)
        return NonEmptyValidator()

    @staticmethod
    def create_phone() -> PhoneValidator:
        return PhoneValidator()

    @staticmethod
    def create_email() -> EmailValidator:
        return EmailValidator()

    @staticmethod
    def create_date() -> DateValidator:
        return DateValidator()

    @staticmethod
    def create_options(options: list[str], error_message: str | None = None) -> OptionsValidator:
        if error_message:
            return OptionsValidator(options, error_message)
        return OptionsValidator(options)

    @staticmethod
    def create_group(error_message: str | None = None) -> GroupValidator:
        if error_message:
            return GroupValidator(error_message)
        return GroupValidator()

    @staticmethod
    def create_yes_no() -> YesNoValidator:
        return YesNoValidator()


# Функции-обертки для обратной совместимости
def validate_non_empty(value: str) -> tuple[bool, str | None]:
    return ValidatorFactory.create_non_empty().validate(value)


def validate_phone(value: str) -> tuple[bool, str | None]:
    return ValidatorFactory.create_phone().validate(value)


def validate_email(value: str) -> tuple[bool, str | None]:
    return ValidatorFactory.create_email().validate(value)


def validate_date(value: str) -> tuple[bool, str | None]:
    return ValidatorFactory.create_date().validate(value)


def validate_yes_no(value: str) -> tuple[bool, str | None]:
    return ValidatorFactory.create_yes_no().validate(value)


def validate_group(value: str) -> tuple[bool, str | None]:
    return ValidatorFactory.create_group().validate(value)


def create_options_validator(options: list[str]) -> Callable[[str], tuple[bool, str | None]]:
    validator = ValidatorFactory.create_options(options)
    return validator.validate
