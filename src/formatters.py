import re

def format_phone(phone):
    # Удаляем все символы, кроме цифр
    phone = re.sub(r'\D', '', phone)
    return phone

def format_date(date):
    # Разбиваем дату на день, месяц и год
    day, month, year = date.split('.')

    # Добавляем ведущие нули, если день или месяц одноразрядные
    day = day.zfill(2)
    month = month.zfill(2)

    # Возвращаем дату в формате dd.mm.yyyy
    return f"{day}.{month}.{year}"
