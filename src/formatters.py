import re

def format_phone_db(phone):
    # Удаляем все символы, кроме цифр
    phone = re.sub(r'\D', '', str(phone))

    if phone.startswith("8"):
        phone = "7" + phone[1:]

    return phone

def format_phone_display(phone):
    phone = format_phone_db(phone)
    return '+' + phone

def format_date(date):
    # Разбиваем дату на день, месяц и год
    day, month, year = date.split('.')

    # Добавляем ведущие нули, если день или месяц одноразрядные
    day = day.zfill(2)
    month = month.zfill(2)

    # Возвращаем дату в формате dd.mm.yyyy
    return f"{day}.{month}.{year}"

def format_probability_display(probability):
    return str(probability) + "%"
