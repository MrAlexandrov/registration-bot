from os import getenv
from dotenv import load_dotenv
from constants import *
from validators import (
    validate_phone,
    validate_email,
    validate_date,
)
from formatters import (
    format_phone_db,
    format_phone_display,
    format_date,
    format_probability_display,
)

load_dotenv()


class Config:
    def __init__(self):
        self.bot_token = getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("Токен не найден! Убедитесь, что файл .env правильно настроен.")

        self.root_id = int(getenv('ROOT_ID'))
        self.lena_id = int(getenv('LENA_ID'))

        self.admin_ids = {self.root_id}
        self.table_getters = self.admin_ids | {self.lena_id}

        self.messages = {
            NAME: "Давай знакомиться, напиши ФИО (в формате Иванов Иван Иванович)",
            BIRTH_DATE: "Когда у тебя день рождения? (в формате 10.03.2002)",
            PHONE: "Напиши свой номер телефона или поделись им из Telegram",
            USERNAME: "Введи свой никнейм в Telegram",
            EMAIL: "Напиши свою почту",
            POSITION: "На какой должности ты хочешь работать в лагере? (можешь выбрать несколько вариантов)",
            DESIRED_AGE: "С детьми какого возраста хочешь работать? (можешь выбрать несколько вариантов)",
            PROBABILITY_INSTRUCTIVE: "Напиши, с какой вероятностью ты сможешь поехать на Инструктив (30.04-03.05)? (только один вариант)",
            PROBABILITY_FIRST: "Напиши, с какой вероятностью ты сможешь поехать на 1 смену (06.06-27.06)?",
            PROBABILITY_SECOND: "С какой вероятностью ты сможешь поехать на 2 смену (04.07-25.07)?",
            EDUCATION_CHOICE: "Где ты учишься?",
            OTHER_EDUCATION: "Укажи название своего учебного заведения",
            STUDY_GROUP: "В какой группе ты учишься?",
            WORK: "Работаешь ли ты?",
            WORK_PLACE: "Напиши, где именно ты работаешь",
            DIPLOM: "Есть ли у тебя диплом?",
            RESCHEDULING_SESSION: "Нужен ли тебе перенос сессии?",
            RESCHEDULING_PRACTICE: "Нужен ли тебе перенос практики?",
            MEDICAL_BOOK: "Есть ли у тебя медицинская книжка?",
            EDIT: "Что хочешь изменить?",
            ADMIN_SEND_MESSAGE: "Напиши сообщение, которое хочешь отправить всем пользователям",
            ADMIN_FEEDBACK_MENU: "Меню обратной связи",
            CREATE_SURVEY_NAME: "Введи название опроса. Оно будет видно только администраторам.",
            CREATE_SURVEY_ADD_QUESTION: "Теперь добавь вопросы к опросу.",
            CREATE_SURVEY_QUESTION_TEXT: "Введи текст вопроса.",
            CREATE_SURVEY_QUESTION_TYPE: "Выбери тип вопроса.",
            CREATE_SURVEY_QUESTION_OPTIONS: "Введи варианты ответов через запятую (например: Да, Нет, Не знаю).",
            ADMIN_SELECT_SURVEY_TO_SEND: "Выбери опрос, который хочешь отправить.",
            ADMIN_VIEW_SURVEY_RESULTS: "Выбери опрос, результаты которого хочешь посмотреть.",
            ADMIN_FILTER_USERS: "Кому отправить опрос?",
        }

        self.labels = {
            NAME: "Имя",
            BIRTH_DATE: "Дата рождения",
            PHONE: "Телефон",
            USERNAME: "Никнейм",
            EMAIL: "Email",
            POSITION: "Желаемая должность",
            DESIRED_AGE: "Желаемый возраст",
            PROBABILITY_INSTRUCTIVE: "Вероятность поехать на Инструктив",
            PROBABILITY_FIRST: "Вероятность поехать на 1 смену",
            PROBABILITY_SECOND: "Вероятность поехать на 2 смену",
            EDUCATION_CHOICE: "Место учёбы",
            OTHER_EDUCATION: "Другое учебное заведение",
            STUDY_GROUP: "Группа",
            WORK: "Работаешь",
            WORK_PLACE: "Место работы",
            DIPLOM: "Диплом",
            RESCHEDULING_SESSION: "Нужен перенос сессии",
            RESCHEDULING_PRACTICE: "Нужен перенос практики",
            MEDICAL_BOOK: "Медицинская книжка",
        }

        self.fields = self._get_fields()
        self.post_registration_states = self._get_post_registration_states()
        self.admin_states = self._get_admin_states()

    def _get_fields(self):
        return [
            {STATE: NAME, LABEL: self.labels[NAME], MESSAGE: self.messages[NAME], EDITABLE: True},
            {STATE: BIRTH_DATE, LABEL: self.labels[BIRTH_DATE], MESSAGE: self.messages[BIRTH_DATE], VALIDATOR: validate_date, DB_FORMATTER: format_date, EDITABLE: True},
            {STATE: PHONE, LABEL: self.labels[PHONE], MESSAGE: self.messages[PHONE], VALIDATOR: validate_phone, DB_FORMATTER: format_phone_db, DISPLAY_FORMATTER: format_phone_display, REQUEST_CONTACT: True, EDITABLE: True},
            {STATE: USERNAME, LABEL: self.labels[USERNAME], MESSAGE: self.messages[USERNAME], VALIDATOR: lambda x: (len(x) > 0, "Имя пользователя не может быть пустым."), DB_FORMATTER: lambda x: x.strip() if x else None, DISPLAY_FORMATTER: lambda x: f"@{x}" if x else "Не указан", EDITABLE: False, AUTO_COLLECT: lambda update: update.message.from_user.username},
            {STATE: EMAIL, LABEL: self.labels[EMAIL], MESSAGE: self.messages[EMAIL], VALIDATOR: validate_email, EDITABLE: True},
            {STATE: POSITION, LABEL: self.labels[POSITION], MESSAGE: self.messages[POSITION], VALIDATOR: lambda x: (x in POSITIONS, "Пожалуйста, выберите один из предложенных вариантов."), MULTI_SELECT: True, OPTIONS: POSITIONS, EDITABLE: True},
            {STATE: DESIRED_AGE, LABEL: self.labels[DESIRED_AGE], MESSAGE: self.messages[DESIRED_AGE], VALIDATOR: lambda x: (x in AGES, "Пожалуйста, выберите один из предложенных вариантов."), MULTI_SELECT: True, OPTIONS: AGES, EDITABLE: True},
            {STATE: PROBABILITY_INSTRUCTIVE, LABEL: self.labels[PROBABILITY_INSTRUCTIVE], MESSAGE: self.messages[PROBABILITY_INSTRUCTIVE], VALIDATOR: lambda x: (x in PERSENTS, "Пожалуйста, выберите один из предложенных вариантов."), OPTIONS: PERSENTS, EDITABLE: True},
            {STATE: PROBABILITY_FIRST, LABEL: self.labels[PROBABILITY_FIRST], MESSAGE: self.messages[PROBABILITY_FIRST], VALIDATOR: lambda x: (x in PERSENTS, "Пожалуйста, выберите один из предложенных вариантов."), OPTIONS: PERSENTS, EDITABLE: True},
            {STATE: PROBABILITY_SECOND, LABEL: self.labels[PROBABILITY_SECOND], MESSAGE: self.messages[PROBABILITY_SECOND], VALIDATOR: lambda x: (x in PERSENTS, "Пожалуйста, выберите один из предложенных вариантов."), OPTIONS: PERSENTS, EDITABLE: True},
            {STATE: EDUCATION_CHOICE, LABEL: self.labels[EDUCATION_CHOICE], MESSAGE: self.messages[EDUCATION_CHOICE], VALIDATOR: lambda x: (x in EDUCATION_OPTIONS, "Пожалуйста, выберите один из предложенных вариантов."), OPTIONS: EDUCATION_OPTIONS, EDITABLE: True},
            {STATE: OTHER_EDUCATION, LABEL: self.labels[OTHER_EDUCATION], MESSAGE: self.messages[OTHER_EDUCATION], SKIP_IF: lambda data: data.get(EDUCATION_CHOICE) != OTHER_STUDY_PLACE, EDITABLE: True},
            {STATE: STUDY_GROUP, LABEL: self.labels[STUDY_GROUP], MESSAGE: self.messages[STUDY_GROUP], VALIDATOR: lambda x: (len(x) > 0, "Название группы не может быть пустым."), SKIP_IF: lambda data: data.get(EDUCATION_CHOICE) in [FINISHED, DO_NOT_STUDY], EDITABLE: True},
            {STATE: WORK, LABEL: self.labels[WORK], MESSAGE: self.messages[WORK], VALIDATOR: lambda x: (x in YES_NO, "Пожалуйста, выберите 'Да' или 'Нет'."), OPTIONS: YES_NO, EDITABLE: True},
            {STATE: WORK_PLACE, LABEL: self.labels[WORK_PLACE], MESSAGE: self.messages[WORK_PLACE], SKIP_IF: lambda data: data.get(WORK) == NO, EDITABLE: True},
            {STATE: DIPLOM, LABEL: self.labels[DIPLOM], MESSAGE: self.messages[DIPLOM], VALIDATOR: lambda x: (x in YES_NO, "Пожалуйста, выберите 'Да' или 'Нет'."), OPTIONS: YES_NO, EDITABLE: True},
            {STATE: RESCHEDULING_SESSION, LABEL: self.labels[RESCHEDULING_SESSION], MESSAGE: self.messages[RESCHEDULING_SESSION], VALIDATOR: lambda x: (x in YES_NO, "Пожалуйста, выберите 'Да' или 'Нет'."), SKIP_IF: lambda data: data.get(EDUCATION_CHOICE) in [FINISHED, DO_NOT_STUDY], OPTIONS: YES_NO, EDITABLE: True},
            {STATE: RESCHEDULING_PRACTICE, LABEL: self.labels[RESCHEDULING_PRACTICE], MESSAGE: self.messages[RESCHEDULING_PRACTICE], VALIDATOR: lambda x: (x in YES_NO, "Пожалуйста, выберите 'Да' или 'Нет'."), SKIP_IF: lambda data: data.get(EDUCATION_CHOICE) in [FINISHED, DO_NOT_STUDY], OPTIONS: YES_NO, EDITABLE: True},
            {STATE: MEDICAL_BOOK, LABEL: self.labels[MEDICAL_BOOK], MESSAGE: self.messages[MEDICAL_BOOK], VALIDATOR: lambda x: (x in YES_NO, "Пожалуйста, выберите 'Да' или 'Нет'."), OPTIONS: YES_NO, EDITABLE: True},
        ]

    def _get_post_registration_states(self):
        def generate_registered_message():
            message = "Отлично! Вот, что я запомнил, проверь, пожалуйста, что всё верно:\n"
            for field in self.fields:
                message += f"{field[LABEL]}: `{{{field[STATE]}}}`\n"
            return message

        return [
            {STATE: REGISTERED, MESSAGE: generate_registered_message(), BUTTONS: [CHANGE_DATA, CREATE_SURVEY]},
            {STATE: EDIT, MESSAGE: self.messages[EDIT], BUTTONS: lambda: [field[LABEL] for field in self.fields] + [CANCEL]},
        ]

    def _get_admin_states(self):
        return [
            {STATE: ADMIN_SEND_MESSAGE, MESSAGE: self.messages[ADMIN_SEND_MESSAGE], BUTTONS: [CANCEL]},
            {STATE: ADMIN_FEEDBACK_MENU, MESSAGE: self.messages[ADMIN_FEEDBACK_MENU], BUTTONS: FEEDBACK_BUTTONS + [CANCEL]},
            {STATE: CREATE_SURVEY_NAME, MESSAGE: self.messages[CREATE_SURVEY_NAME], BUTTONS: [CANCEL]},
            {STATE: CREATE_SURVEY_ADD_QUESTION, MESSAGE: self.messages[CREATE_SURVEY_ADD_QUESTION], BUTTONS: [ADD_QUESTION, FINISH_SURVEY_CREATION]},
            {STATE: CREATE_SURVEY_QUESTION_TEXT, MESSAGE: self.messages[CREATE_SURVEY_QUESTION_TEXT], BUTTONS: [CANCEL]},
            {STATE: CREATE_SURVEY_QUESTION_TYPE, MESSAGE: self.messages[CREATE_SURVEY_QUESTION_TYPE], OPTIONS: QUESTION_TYPE_OPTIONS},
            {STATE: CREATE_SURVEY_QUESTION_OPTIONS, MESSAGE: self.messages[CREATE_SURVEY_QUESTION_OPTIONS], BUTTONS: [CANCEL]},
            {STATE: ADMIN_SELECT_SURVEY_TO_SEND, MESSAGE: self.messages[ADMIN_SELECT_SURVEY_TO_SEND], BUTTONS: [SEND_TO_ALL, SEND_TO_FILTERED, CANCEL]},
            {STATE: ADMIN_VIEW_SURVEY_RESULTS, MESSAGE: self.messages[ADMIN_VIEW_SURVEY_RESULTS], BUTTONS: [CANCEL]},
            {STATE: ADMIN_FILTER_USERS, MESSAGE: self.messages[ADMIN_FILTER_USERS], BUTTONS: [CANCEL]},
        ]


config = Config()
