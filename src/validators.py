import re
from formatters import format_phone_db


def validate_phone(phone):
    phone = format_phone_db(phone)
    pattern = r'^(7)\d{10}$'
    if not re.match(pattern, phone):
        return False, "Неверный формат номера телефона. Пожалуйста, введите номер в формате +7 (XXX) XXX-XX-XX или 8 (XXX) XXX-XX-XX."
    return True, None


def validate_email(email):
    """Проверяет, что это корректный email."""
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return False, "Неверный формат email. Пожалуйста, введите корректный email."
    return True, None


def validate_date(date):
    pattern = r'^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\.(19|20)\d{2}$'
    if not re.match(pattern, date):
        return False, "Неверный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ."
    return True, None


def validate_probability(probability):
    try:
        prob = int(probability)
        if not (0 <= prob <= 100):
            return False, "Вероятность должна быть числом от 0 до 100."
    except ValueError:
        return False, "Вероятность должна быть числом."
    return True, None
