from telegram import ReplyKeyboardMarkup, KeyboardButton

ABOUT_TRIP = "O выезде"
WHAT_TO_TAKE = "Что взять?"
CHANGE_DATA = "Изменить данные"
SHOW_DATA = "Показать данные"

main_menu_keyboard = ReplyKeyboardMarkup(
    [
        [ABOUT_TRIP, WHAT_TO_TAKE],
        [SHOW_DATA, CHANGE_DATA]
    ],
    one_time_keyboard=True
)

ask_phone_number_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]],
    one_time_keyboard=True
)

CHANGE_FIO_BUTTON="ФИО"
CHANGE_BIRTH_DAY_BUTTON="День рождения"
CHANGE_GROUP_BUTTON="Группу"
CHANGE_PHONE_NUBER_BUTTON="Номер телефона"
CHANGE_EXPECTATIONS_BUTTON="Ожидания"
CHANGE_FOOD_WISHES_BUTTON="Особенности питания"
CHANGE_BACK="Назад"

change_data_keyboard = ReplyKeyboardMarkup(
    [
        [CHANGE_FIO_BUTTON, CHANGE_BIRTH_DAY_BUTTON],
        [CHANGE_GROUP_BUTTON, CHANGE_PHONE_NUBER_BUTTON],
        [CHANGE_EXPECTATIONS_BUTTON, CHANGE_FOOD_WISHES_BUTTON],
        [CHANGE_BACK]
    ],
    one_time_keyboard=True
)

answer_no = ["Нет"]
answer_no_keyboard = ReplyKeyboardMarkup([answer_no], one_time_keyboard=True)

# markup_answer_no = ReplyKeyboardMarkup([answer_no], one_time_keyboard=True)
