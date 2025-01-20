import re

def normalize_phone(phone):
    # Удаляем все символы, кроме цифр
    phone = re.sub(r'\D', '', phone)
    return phone
