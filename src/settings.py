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

MESSAGES = {
    "name":                     """Давай знакомиться, напиши ФИО (в формате Иванов Иван Иванович)""",
    "birth_date":               """Когда у тебя день рождения? (в формате 10.03.2002)""",
    "phone":                    """Напиши свой номер телефона или поделись им из Telegram""",
    "username":                 """Введи свой никнейм в Telegram""",
    "email":                    """Напиши свою почту""",
    "position":                 """На какой должности ты хочешь работать в лагере? (можешь выбрать несколько вариантов)""",
    "desired_age":              """С детьми какого возраста хочешь работать? (можешь выбрать несколько вариантов)""",
    "probability_instructive":  """Напиши, с какой вероятностью ты сможешь поехать на Инструктив (30.04-03.05)? (только один вариант)""",
    "probability_first":        """Напиши, с какой вероятностью ты сможешь поехать на 1 смену (06.06-27.06)?""",
    "probability_second":       """С какой вероятностью ты сможешь поехать на 2 смену (04.07-25.07)?""",
    "education_choice":         """Где ты учишься?""",
    "other_education":          """Укажи название своего учебного заведения""",
    "study_group":              """В какой группе ты учишься?""",
    "work":                     """Работаешь ли ты?""",
    "work_place":               """Напиши, где именно ты работаешь""",
    "diplom":                   """Есть ли у тебя диплом?""",
    "rescheduling_session":     """Нужен ли тебе перенос сессии?""",
    "rescheduling_practice":    """Нужен ли тебе перенос практики?""",
    "medical_book":             """Есть ли у тебя медицинская книжка?""",
    # "next_field":               """""",
}

# {
#     "name":                 "next_field",
#     "label":                "label_that_user_will_see",
#     "message":              MESSAGES["next_field"],
#     "validator":            lambda x: len(x) > 0,
#     "db_formatter":         None,                         # function that will process the data before entering it into the database
#     "display_formatter":    None,                         # function that will process data from the database before displaying it
#     "type":                 "TEXT",                       # the type in which the data will be stored 
#     "request_contact":      True,                         # to collect a contact via the telegram api
#     "options":              ["First", "Second"],          # inline buttons
#     "multi_select":         True,                         # oppotunity to select several options (default False)
# },

FIELDS = [
    {
        "name":                 "name",
        "label":                "Имя",
        "message":              MESSAGES["name"],
    },
    {
        "name":                 "birth_date",
        "label":                "Дата рождения",
        "message":              MESSAGES["birth_date"],
        "validator":            validate_date,
        "db_formatter":         format_date,
    },
    {
        "name":                 "phone",
        "label":                "Телефон",
        "message":              MESSAGES["phone"],
        "validator":            validate_phone,
        "db_formatter":         format_phone_db,
        "display_formatter":    format_phone_display,
        "request_contact":      True
    },
    {
        "name":                 "username",
        "label":                "Никнейм",
        "message":              MESSAGES["username"],
        "validator":            lambda x: len(x) > 0,
        "db_formatter":         lambda x: x.strip() if x else None,
        "display_formatter":    lambda x: f"@{x}" if x else "Не указан",
        "formatter":            lambda x: x.strip(),
    },
    {
        "name":                 "email",
        "label":                "Email",
        "message":              MESSAGES["email"],
        "validator":            validate_email,
    },
    {
        "name":                 "position",
        "label":                "Желаемая должность",
        "message":              MESSAGES["position"],
        "validator":            lambda x: len(x) > 0,
        "db_formatter":         lambda x: ", ".join(x) if isinstance(x, list) else x,
        "display_formatter":    lambda x: ", ".join(x) if isinstance(x, list) else x,
        "multi_select":         True,
        "options":              ["Вожатый", "Подменка", "Физрук", "Кружковод", "Фотограф", "Радист", "Культорг"],
    },
    {
        "name":                 "desired_age",
        "label":                "Желаемый возраст",
        "message":              MESSAGES["desired_age"],
        "db_formatter":         lambda x: ", ".join(x) if isinstance(x, list) else x,
        "display_formatter":    lambda x: ", ".join(x) if isinstance(x, list) else x,
        "multi_select":         True,
        "options":              ["6-9", "10-12", "12-14", "14-16"],
    },
    {
        "name":                 "probability_instructive",
        "label":                "Вероятность поехать на Инструктив",
        "message":              MESSAGES["probability_instructive"],
        "display_formatter":    format_probability_display,
        "options":              ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        "name":                 "probability_first",
        "label":                "Вероятность поехать на 1 смену",
        "message":              MESSAGES["probability_first"],
        "display_formatter":    format_probability_display,
        "options":              ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        "name":                 "probability_second",
        "label":                "Вероятность поехать на 2 смену",
        "message":              MESSAGES["probability_second"],
        "display_formatter":    format_probability_display,
        "options":              ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        "name":                 "education_choice",
        "label":                "Место учёбы",
        "message":              MESSAGES["education_choice"],
        "validator":            lambda x: len(x) > 0,
        "options":              ["МГТУ им. Баумана", "Другое учебное заведение", "Закончил(а)", "Не учусь"],
    },
    {
        "name":                 "other_education",
        "label":                "Другое учебное заведение",
        "message":              MESSAGES["other_education"],
    },
    {
        "name":                 "study_group",
        "label":                "Группа",
        "message":              MESSAGES["study_group"],
        "validator":            lambda x: len(x) > 0,
    },
    {
        "name":                 "work",
        "label":                "Работаешь",
        "message":              MESSAGES["work"],
        "display_formatter":    lambda x: "Да" if x == "Да" else "Нет",
        "options":              ["Да", "Нет"],
    },
    {
        "name":                 "work_place",
        "label":                "Место работы",
        "message":              MESSAGES["work_place"],
    },
    {
        "name":                 "diplom",
        "label":                "Диплом",
        "message":              MESSAGES["diplom"],
        "display_formatter":    lambda x: "Есть" if x == "Да" else "Нет",
        "options":              ["Да", "Нет"],
    },
    {
        "name":                 "rescheduling_session",
        "label":                "Нужен перенос сессии",
        "message":              MESSAGES["rescheduling_session"],
        "display_formatter":    lambda x: "Нужен" if x == "Да" else "Не нужен",
        "options":              ["Да", "Нет"],
    },
    {
        "name":                 "rescheduling_practice",
        "label":                "Нужен перенос практики",
        "message":              MESSAGES["rescheduling_practice"],
        "display_formatter":    lambda x: "Нужен" if x == "Да" else "Не нужен",
        "options":              ["Да", "Нет"],
    },
    {
        "name":                 "medical_book",
        "label":                "Медицинская книжка",
        "message":              MESSAGES["medical_book"],
        "display_formatter":    lambda x: "Есть" if x == "Да" else "Нет",
        "options":              ["Да", "Нет"],
    },
]

def generate_registered_message():
    """Генерирует сообщение о регистрации на основе FIELDS."""
    message = "Отлично! Вот, что я запомнил, проверь, пожалуйста, что всё верно:\n"
    for field in FIELDS:
        message += f"{field['label']}: `{{{field['name']}}}`\n"
    return message


POST_REGISTRATION_STATES = [
    {
        "name":                 "registered",
        "message":              generate_registered_message(),
        "buttons":              ["Изменить данные"],
    },
    {
        "name":                 "edit",
        "message":              "Что хочешь изменить?",
        "buttons":              lambda: [field["label"] for field in FIELDS] + ["Отмена"],
    },
]
