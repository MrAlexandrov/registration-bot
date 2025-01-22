from os import getenv
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменной окружения
BOT_TOKEN = getenv('TEST_BOT_TOKEN')

# BOT_TOKEN = getenv('RELEASE_BOT_TOKEN')
ROOT_ID = int(getenv('ROOT_ID'))

if BOT_TOKEN is None:
    raise ValueError("Токен не найден! Убедитесь, что файл .env правильно настроен.")

if ROOT_ID is None:
    raise ValueError("ROOT_ID не найден")

ADMIN_IDS = []

from validators import (
    validate_phone,
    validate_email,
    validate_date,
    validate_probability,
)
from formatters import (
    format_phone_db,
    format_phone_display,

    format_date,

    format_probability_display,
)

FIELDS = [
    {
        "name":                 "name",
        "label":                "Имя",
        "message":              "Давай знакомиться, напиши ФИО (в формате Иванов Иван Иванович)",
        "validator":            lambda x: len(x) > 0,
        "db_formatter":         None,                               # Для БД
        "display_formatter":    None,                               # Для вывода
        "formatter":            None,
        "type":                 "TEXT",
    },
    {
        "name":                 "birth_date",
        "label":                "Дата рождения",
        "message":              "Когда у тебя день рождения? (в формате 10.03.2002)",
        "validator":            validate_date,
        "db_formatter":         format_date,
        "display_formatter":    None,
        "type": "TEXT",
    },
    {
        "name":                 "phone",
        "label":                "Телефон",
        "message":              "Напиши свой номер телефона или поделись им из Telegram",
        "validator":            validate_phone,
        "db_formatter":         format_phone_db,
        "display_formatter":    format_phone_display,
        "type":                 "TEXT",
        "request_contact":      True
    },
    {
        "name":                 "username",
        "label":                "Никнейм",
        "message":              "Введи свой никнейм в Telegram",
        "type":                 "TEXT",
        "validator":            lambda x: len(x) > 0,  # Убедиться, что введено хотя бы что-то
        "db_formatter":         lambda x: x.strip() if x else None,
        "display_formatter":    lambda x: f"@{x}" if x else "Не указан",
        "formatter":            lambda x: x.strip(),
    },
    {
        "name":                 "email",
        "label":                "Email",
        "message":              "Напиши свою почту",
        "validator":            validate_email,
        "db_formatter":         None,
        "display_formatter":    None,
        "type":                 "TEXT",
    },
    {
        "name":                 "position",
        "label":                "Желаемая должность",
        "message":              "На какой должности ты хочешь работать в лагере? (можешь выбрать несколько вариантов)",
        "validator":            lambda x: len(x) > 0,
        "db_formatter":         lambda x: ", ".join(x) if isinstance(x, list) else x,
        "display_formatter":    lambda x: ", ".join(x) if isinstance(x, list) else x,
        "type":                 "TEXT",
        "multi_select":         True,
        "options":              ["Вожатый", "Подменка", "Физрук", "Кружковод", "Фотограф", "Радист"],
    },
    {
        "name":                 "desired_age",
        "label":                "Желаемый возраст",
        "message":              "С детьми какого возраста хочешь работать? (можешь выбрать несколько вариантов)",
        "validator":            None,
        "db_formatter":         lambda x: ", ".join(x) if isinstance(x, list) else x,
        "display_formatter":    lambda x: ", ".join(x) if isinstance(x, list) else x,
        "type":                 "TEXT",
        "multi_select":         True,
        "options":              ["1-9", "10-12", "12-14", "14-16"],
    },
    {
        "name":                 "probability_instructive",
        "label":                "Вероятность поехать на Инструктив",
        "message":              "Напиши, с какой вероятностью ты сможешь поехать на Инструктив? (только один вариант)",
        "validator":            validate_probability,
        "db_formatter":         None,
        "display_formatter":    format_probability_display,
        "type":                 "TEXT",
        "multi_select":         False,
        "options":              ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        "name":                 "probability_first",
        "label":                "Вероятность поехать на 1 смену",
        "message":              "Напиши, с какой вероятностью ты сможешь поехать на 1 смену? (только один вариант)",
        "validator":            validate_probability,
        "db_formatter":         None,
        "display_formatter":    format_probability_display,
        "type":                 "TEXT",
        "multi_select":         False,
        "options":              ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        "name":                 "probability_second",
        "label":                "Вероятность поехать на 2 смену",
        "message":              "С какой вероятностью ты сможешь поехать на 2 смену? (только один вариант)",
        "validator":            validate_probability,
        "db_formatter":         None,
        "display_formatter":    format_probability_display,
        "type":                 "TEXT",
        "multi_select":         False,
        "options":              ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        "name":                 "university",
        "label":                "Университет",
        "message":              "В каком университете ты учишься?",
        "validator":            lambda x: len(x) > 0,
        "db_formatter":         None,
        "display_formatter":    None,
        "formatter":            None,
        "type":                 "TEXT",
    },
    {
        "name":                 "study_group",
        "label":                "Группа",
        "message":              "В какой группе ты учишься?",
        "validator":            lambda x: len(x) > 0,
        "db_formatter":         None,
        "display_formatter":    None,
        "formatter":            None,
        "type":                 "TEXT",
    },
    {
        "name":                 "work",
        "label":                "Место работы",
        "message":              "Напиши место работы (если не работаешь, отправь Нет)",
        "validator":            lambda x: len(x) > 0,
        "db_formatter":         None,
        "display_formatter":    None,
        "formatter":            None,
        "type":                 "TEXT",
    },
    {
        "name":                 "diplom",
        "label":                "Диплом",
        "message":              "Напиши, есть ли у тебя диплом?",
        "validator":            None,
        "db_formatter":         None,
        "display_formatter":    lambda x: "Есть" if x == "Да" else "Нет",
        "formatter":            None,
        "type":                 "TEXT",
        "multi_select": False,
        "options": ["Да", "Нет"],  # Возможные варианты
    },
    {
        "name":                 "rescheduling_session",
        "label":                "Нужен перенос сессии",
        "message":              "Нужен ли тебе перенос сессии?",
        "validator":            None,
        "db_formatter":         None,
        "display_formatter":    lambda x: "Нужен" if x == "Да" else "Не нужен",
        "formatter":            None,
        "type":                 "TEXT",
        "multi_select": False,
        "options": ["Да", "Нет"],  # Возможные варианты
    },
    {
        "name":                 "rescheduling_practice",
        "label":                "Нужен перенос практики",
        "message":              "Нужен ли тебе перенос практики?",
        "validator":            None,
        "db_formatter":         None,
        "display_formatter":    lambda x: "Нужен" if x == "Да" else "Не нужен",
        "formatter":            None,
        "type":                 "TEXT",
        "multi_select": False,
        "options": ["Да", "Нет"],  # Возможные варианты
    },
    {
        "name":                 "medical_book",
        "label":                "Медицинская книжка",
        "message":              "Есть ли у тебя медицинская книжка? (она должна быть действительна по конец последнего рабочего дня на смене)",
        "validator":            None,
        "db_formatter":         None,
        "display_formatter":    lambda x: "Есть" if x == "Да" else "Нет",
        "formatter":            None,
        "type":                 "TEXT",
        "multi_select": False,
        "options": ["Да", "Нет"],  # Возможные варианты
    },
]

def generate_registered_message():
    """Генерирует сообщение о регистрации на основе FIELDS."""
    message = "Отлично! Вот, что я запомнил:\n"
    for field in FIELDS:
        message += f"{field['label']}: `{{{field['name']}}}`\n"  # <-- правильная подстановка
    return message


POST_REGISTRATION_STATES = [
    {
        "name":                 "registered",
        "message":              generate_registered_message(),
        "buttons":              ["Изменить данные"],  # Здесь можно добавить любые действия
    },
    {
        "name":                 "edit",
        "message":              "Что хочешь изменить?",
        "buttons":              lambda: [field["label"] for field in FIELDS] + ["Отмена"],   
    },
]
