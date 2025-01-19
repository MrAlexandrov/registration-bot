import re

def validate_date(date):
    pattern = r'^(0?[1-9]|[12][0-9]|3[01])\.(0?[1-9]|1[0-2])\.(19|20)\d{2}$'
    return bool(re.match(pattern, date))

def validate_group(group):
    pattern = r'^[а-яА-Я]{1,5}\d{0,2}[сицСИЦ]?-([1-9]|1[0-6])[1-9]([абмтАБМТ]?[вВ]?)$'
    return bool(re.match(pattern, group))

def validate_phone(phone):
    # Удаляем все символы, кроме цифр
    phone = re.sub(r'\D', '', phone)
    
    # Проверяем, соответствует ли номер формату
    pattern = r'^(7|8)\d{10}$'
    return bool(re.match(pattern, phone))
