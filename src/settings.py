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

# {
#     "name":                 "name",
#     "label":                "label",
#     "message":              "message",
#     "validator":            lambda x: len(x) > 0,
#     "db_formatter":         None,                               # Для БД
#     "display_formatter":    None,                               # Для вывода
#     "formatter":            None,                               # ???
#     "display_formatter":    None,
#     "type":                 "TEXT",
#     "request_contact":      True,
#     "multi_select":         True,
#     "options":              ["First", "Second"],
# },

FIELDS = [
    {
        "name":                 "name",
        "label":                "Имя",
        "message":              "Давай знакомиться, напиши ФИО (в формате Иванов Иван Иванович)",
        "type":                 "TEXT",
    },
    {
        "name":                 "birth_date",
        "label":                "Дата рождения",
        "message":              "Когда у тебя день рождения? (в формате 10.03.2002)",
        "validator":            validate_date,
        "db_formatter":         format_date,
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
        "db_formatter":         lambda x: ", ".join(x) if isinstance(x, list) else x,
        "display_formatter":    lambda x: ", ".join(x) if isinstance(x, list) else x,
        "type":                 "TEXT",
        "multi_select":         True,
        "options":              ["6-9", "10-12", "12-14", "14-16"],
    },
    {
        "name":                 "probability_instructive",
        "label":                "Вероятность поехать на Инструктив",
        "message":              "Напиши, с какой вероятностью ты сможешь поехать на Инструктив? (только один вариант)",
        "validator":            validate_probability,
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
        "display_formatter":    format_probability_display,
        "type":                 "TEXT",
        "multi_select":         False,
        "options":              ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        "name":                 "education_choice",
        "label":                "Место учёбы",
        "message":              "Где ты учишься?",
        "validator":            lambda x: len(x) > 0,
        "type":                 "TEXT",
        "multi_select":         False,
        "options":              ["МГТУ им. Баумана", "Другое учебное заведение", "Закончил(а)", "Не учусь"],
    },
    {
        "name":                 "other_education",
        "label":                "Другое учебное заведение",
        "message":              "Укажи название своего учебного заведения",
        "type":                 "TEXT",
    },
    {
        "name":                 "study_group",
        "label":                "Группа",
        "message":              "В какой группе ты учишься?",
        "validator":            lambda x: len(x) > 0,
        "type":                 "TEXT",
    },
    {
        "name":                 "work",
        "label":                "Работаешь",
        "message":              "Работаешь ли ты?",
        "display_formatter":    lambda x: "Да" if x == "Да" else "Нет",
        "type":                 "TEXT",
        "multi_select":         False,
        "options":              ["Да", "Нет"],  # Возможные варианты
    },
    {
        "name":                 "work_place",
        "label":                "Место работы",
        "message":              "Напиши, где именно ты работаешь",
        "type":                 "TEXT",
    },
    {
        "name":                 "diplom",
        "label":                "Диплом",
        "message":              "Есть ли у тебя диплом?",
        "display_formatter":    lambda x: "Есть" if x == "Да" else "Нет",
        "type":                 "TEXT",
        "multi_select": False,
        "options": ["Да", "Нет"],  # Возможные варианты
    },
    {
        "name":                 "rescheduling_session",
        "label":                "Нужен перенос сессии",
        "message":              "Нужен ли тебе перенос сессии?",
        "display_formatter":    lambda x: "Нужен" if x == "Да" else "Не нужен",
        "type":                 "TEXT",
        "multi_select": False,
        "options": ["Да", "Нет"],  # Возможные варианты
    },
    {
        "name":                 "rescheduling_practice",
        "label":                "Нужен перенос практики",
        "message":              "Нужен ли тебе перенос практики?",
        "display_formatter":    lambda x: "Нужен" if x == "Да" else "Не нужен",
        "type":                 "TEXT",
        "multi_select": False,
        "options": ["Да", "Нет"],  # Возможные варианты
    },
    {
        "name":                 "medical_book",
        "label":                "Медицинская книжка",
        "message":              "Есть ли у тебя медицинская книжка?",
        "display_formatter":    lambda x: "Есть" if x == "Да" else "Нет",
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
