import re
from formatters import format_phone

def validate_date(date):
    pattern = r'^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\.(19|20)\d{2}$'
    return bool(re.match(pattern, date))

def validate_group(group):
    pattern = r'^[а-яА-Я]{1,5}\d{0,2}[сицСИЦ]?-([1-9]|1[0-6])[1-9]([абмтАБМТ]?[вВ]?)$'
    return bool(re.match(pattern, group))

def validate_phone(phone):
    phone = format_phone(phone)
    # Проверяем, соответствует ли номер формату
    pattern = r'^(7|8)\d{10}$'
    return bool(re.match(pattern, phone))

def validate_name(name):
    return True

def validate_email(email):
    """Проверяет, что это корректный email."""
    return bool(re.match(r"^[^@]+@[^@]+\.[^@]+$", email))

def validate_age(age):
    """Проверяет, что возраст — это число от 1 до 120."""
    try:
        age = int(age)
        return 1 <= age <= 120
    except ValueError:
        return False
