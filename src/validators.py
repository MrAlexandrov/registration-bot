import re
from formatters import format_phone_db


def validate_phone(phone):
    phone = format_phone_db(phone)
    # Проверяем, соответствует ли номер формату
    pattern = r'^(7)\d{10}$'
    return bool(re.match(pattern, phone))

def validate_email(email):
    """Проверяет, что это корректный email."""
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))

def validate_date(date):
    pattern = r'^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\.(19|20)\d{2}$'
    return bool(re.match(pattern, date))

def validate_probability(probability):
    try:
        probability = int(probability)
        return 0 <= probability <= 100
    except ValueError:
        return False
