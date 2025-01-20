import re

def format_phone(phone):
    # Удаляем все символы, кроме цифр
    phone = re.sub(r'\D', '', phone)
    return phone
