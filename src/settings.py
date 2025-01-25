from os import getenv
from dotenv import load_dotenv
from constants import *

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем токен бота из переменной окружения
BOT_TOKEN = getenv('BOT_TOKEN')

# BOT_TOKEN = getenv('RELEASE_BOT_TOKEN')
ROOT_ID = int(getenv('ROOT_ID'))
LENA_ID = int(getenv('LENA_ID'))

if BOT_TOKEN is None:
    raise ValueError("Токен не найден! Убедитесь, что файл .env правильно настроен.")

if ROOT_ID is None:
    raise ValueError("ROOT_ID не найден")

ADMIN_IDS = {
    ROOT_ID,
}

TABLE_GETTERS = ADMIN_IDS | {
    LENA_ID,
}

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
    NAME:                       """Давай знакомиться, напиши ФИО (в формате Иванов Иван Иванович)""",
    BIRTH_DATE:                 """Когда у тебя день рождения? (в формате 10.03.2002)""",
    PHONE:                      """Напиши свой номер телефона или поделись им из Telegram""",
    USERNAME:                   """Введи свой никнейм в Telegram""",
    EMAIL:                      """Напиши свою почту""",
    POSITION:                   """На какой должности ты хочешь работать в лагере? (можешь выбрать несколько вариантов)""",
    DESIRED_AGE:                """С детьми какого возраста хочешь работать? (можешь выбрать несколько вариантов)""",
    PROBABILITY_INSTRUCTIVE:    """Напиши, с какой вероятностью ты сможешь поехать на Инструктив (30.04-03.05)? (только один вариант)""",
    PROBABILITY_FIRST:          """Напиши, с какой вероятностью ты сможешь поехать на 1 смену (06.06-27.06)?""",
    PROBABILITY_SECOND:         """С какой вероятностью ты сможешь поехать на 2 смену (04.07-25.07)?""",
    EDUCATION_CHOICE:           """Где ты учишься?""",
    OTHER_EDUCATION:            """Укажи название своего учебного заведения""",
    STUDY_GROUP:                """В какой группе ты учишься?""",
    WORK:                       """Работаешь ли ты?""",
    WORK_PLACE:                 """Напиши, где именно ты работаешь""",
    DIPLOM:                     """Есть ли у тебя диплом?""",
    RESCHEDULING_SESSION:       """Нужен ли тебе перенос сессии?""",
    RESCHEDULING_PRACTICE:      """Нужен ли тебе перенос практики?""",
    MEDICAL_BOOK:               """Есть ли у тебя медицинская книжка?""",
    # NEXT_FIELD:               """""",

    EDIT:                       """Что хочешь изменить?""",
    ADMIN_SEND_MESSAGE:         """Напиши сообщение, которое хочешь отправить всем пользователям"""
}

LABELS = {
    NAME:                       "Имя",
    BIRTH_DATE:                 "Дата рождения",
    PHONE:                      "Телефон",
    USERNAME:                   "Никнейм",
    EMAIL:                      "Email",
    POSITION:                   "Желаемая должность",
    DESIRED_AGE:                "Желаемый возраст",
    PROBABILITY_INSTRUCTIVE:    "Вероятность поехать на Инструктив",
    PROBABILITY_FIRST:          "Вероятность поехать на 1 смену",
    PROBABILITY_SECOND:         "Вероятность поехать на 2 смену",
    EDUCATION_CHOICE:           "Место учёбы",
    OTHER_EDUCATION:            "Другое учебное заведение",
    STUDY_GROUP:                "Группа",
    WORK:                       "Работаешь",
    WORK_PLACE:                 "Место работы",
    DIPLOM:                     "Диплом",
    RESCHEDULING_SESSION:       "Нужен перенос сессии",
    RESCHEDULING_PRACTICE:      "Нужен перенос практики",
    MEDICAL_BOOK:               "Медицинская книжка",
}

# {
#     STATE:                  NEXT_FIELD,
#     LABEL:                  "label_that_user_will_see",
#     MESSAGE:                MESSAGES[NEXT_FIELD],
#     VALIDATOR:              lambda x: len(x) > 0,
#     DB_FORMATTER:           None,                         # function that will process the data before entering it into the database
#     DISPLAY_FORMATTER:      None,                         # function that will process data from the database before displaying it
#     TYPE:                   "TEXT",                       # the type in which the data will be stored 
#     REQUEST_CONTACT:        True,                         # to collect a contact via the telegram api
#     OPTIONS:                ["First", "Second"],          # inline buttons
#     MULTI_SELECT:           True,                         # oppotunity to select several options (default False)
# },



FIELDS = [
    {
        STATE:                  NAME,
        LABEL:                  LABELS[NAME],
        MESSAGE:                MESSAGES[NAME],
    },
    {
        STATE:                  BIRTH_DATE,
        LABEL:                  LABELS[BIRTH_DATE],
        MESSAGE:                MESSAGES[BIRTH_DATE],
        VALIDATOR:              validate_date,
        DB_FORMATTER:           format_date,
    },
    {
        STATE:                  PHONE,
        LABEL:                  LABELS[PHONE],
        MESSAGE:                MESSAGES[PHONE],
        VALIDATOR:              validate_phone,
        DB_FORMATTER:           format_phone_db,
        DISPLAY_FORMATTER:      format_phone_display,
        REQUEST_CONTACT:        True
    },
    {
        STATE:                  USERNAME,
        LABEL:                  LABELS[USERNAME],
        MESSAGE:                MESSAGES[USERNAME],
        VALIDATOR:              lambda x: len(x) > 0,
        DB_FORMATTER:           lambda x: x.strip() if x else None,
        DISPLAY_FORMATTER:      lambda x: f"@{x}" if x else "Не указан",
        # "formatter":            lambda x: x.strip(),
    },
    {
        STATE:                  EMAIL,
        LABEL:                  LABELS[EMAIL],
        MESSAGE:                MESSAGES[EMAIL],
        VALIDATOR:              validate_email,
    },
    {
        STATE:                  POSITION,
        LABEL:                  LABELS[POSITION],
        MESSAGE:                MESSAGES[POSITION],
        VALIDATOR:              lambda x: len(x) > 0,
        DB_FORMATTER:           lambda x: ", ".join(x) if isinstance(x, list) else x,
        DISPLAY_FORMATTER:      lambda x: ", ".join(x) if isinstance(x, list) else x,
        MULTI_SELECT:           True,
        OPTIONS:                ["Вожатый", "Подменка", "Физрук", "Кружковод", "Фотограф", "Радист", "Культорг"],
    },
    {
        STATE:                  DESIRED_AGE,
        LABEL:                  LABELS[DESIRED_AGE],
        MESSAGE:                MESSAGES[DESIRED_AGE],
        DB_FORMATTER:           lambda x: ", ".join(x) if isinstance(x, list) else x,
        DISPLAY_FORMATTER:      lambda x: ", ".join(x) if isinstance(x, list) else x,
        MULTI_SELECT:           True,
        OPTIONS:                ["6-9", "10-12", "12-14", "14-16"],
    },
    {
        STATE:                  PROBABILITY_INSTRUCTIVE,
        LABEL:                  LABELS[PROBABILITY_INSTRUCTIVE],
        MESSAGE:                MESSAGES[PROBABILITY_INSTRUCTIVE],
        DISPLAY_FORMATTER:      format_probability_display,
        OPTIONS:                ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        STATE:                  PROBABILITY_FIRST,
        LABEL:                  LABELS[PROBABILITY_FIRST],
        MESSAGE:                MESSAGES[PROBABILITY_FIRST],
        DISPLAY_FORMATTER:      format_probability_display,
        OPTIONS:                ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        STATE:                  PROBABILITY_SECOND,
        LABEL:                  LABELS[PROBABILITY_SECOND],
        MESSAGE:                MESSAGES[PROBABILITY_SECOND],
        DISPLAY_FORMATTER:      format_probability_display,
        OPTIONS:                ["0-25", "25-50", "50-75", "75-100"],
    },
    {
        STATE:                  EDUCATION_CHOICE,
        LABEL:                  LABELS[EDUCATION_CHOICE],
        MESSAGE:                MESSAGES[EDUCATION_CHOICE],
        VALIDATOR:              lambda x: len(x) > 0,
        OPTIONS:                [BMSTU, OTHER_STUDY_PLACE, FINISHED, DO_NOT_STUDY],
    },
    {
        STATE:                  OTHER_EDUCATION,
        LABEL:                  LABELS[OTHER_EDUCATION],
        MESSAGE:                MESSAGES[OTHER_EDUCATION],
    },
    {
        STATE:                  STUDY_GROUP,
        LABEL:                  LABELS[STUDY_GROUP],
        MESSAGE:                MESSAGES[STUDY_GROUP],
        VALIDATOR:              lambda x: len(x) > 0,
    },
    {
        STATE:                  WORK,
        LABEL:                  LABELS[WORK],
        MESSAGE:                MESSAGES[WORK],
        DISPLAY_FORMATTER:      lambda x: YES if x == YES else NO,
        OPTIONS:                [YES, NO],
    },
    {
        STATE:                  WORK_PLACE,
        LABEL:                  LABELS[WORK_PLACE],
        MESSAGE:                MESSAGES[WORK_PLACE],
    },
    {
        STATE:                  DIPLOM,
        LABEL:                  LABELS[DIPLOM],
        MESSAGE:                MESSAGES[DIPLOM],
        DISPLAY_FORMATTER:      lambda x: "Есть" if x == YES else NO,
        OPTIONS:                [YES, NO],
    },
    {
        STATE:                  RESCHEDULING_SESSION,
        LABEL:                  LABELS[RESCHEDULING_SESSION],
        MESSAGE:                MESSAGES[RESCHEDULING_SESSION],
        DISPLAY_FORMATTER:      lambda x: "Нужен" if x == YES else "Не нужен",
        OPTIONS:                [YES, NO],
    },
    {
        STATE:                  RESCHEDULING_PRACTICE,
        LABEL:                  LABELS[RESCHEDULING_PRACTICE],
        MESSAGE:                MESSAGES[RESCHEDULING_PRACTICE],
        DISPLAY_FORMATTER:      lambda x: "Нужен" if x == YES else "Не нужен",
        OPTIONS:                [YES, NO],
    },
    {
        STATE:                  MEDICAL_BOOK,
        LABEL:                  LABELS[MEDICAL_BOOK],
        MESSAGE:                MESSAGES[MEDICAL_BOOK],
        DISPLAY_FORMATTER:      lambda x: "Есть" if x == YES else NO,
        OPTIONS:                [YES, NO],
    },
]

def generate_registered_message():
    """Генерирует сообщение о регистрации на основе FIELDS."""
    message = "Отлично! Вот, что я запомнил, проверь, пожалуйста, что всё верно:\n"
    for field in FIELDS:
        message += f"{field[LABEL]}: `{{{field[STATE]}}}`\n"
    return message


POST_REGISTRATION_STATES = [
    {
        STATE:                  REGISTERED,
        MESSAGE:                generate_registered_message(),
        BUTTONS:                [CHANGE_DATA],
    },
    {
        STATE:                  EDIT,
        MESSAGE:                MESSAGES[EDIT],
        BUTTONS:                lambda: [field[LABEL] for field in FIELDS] + [CANCEL],
    },
]

ADMIN_STATES = [
    {
        STATE:                  ADMIN_SEND_MESSAGE,
        MESSAGE:                MESSAGES[ADMIN_SEND_MESSAGE],
        BUTTONS:                [CANCEL]
    },
]
