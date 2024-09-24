from telegram import ReplyKeyboardMarkup, KeyboardButton

ABOUT_TRIP = "O выезде"
WHAT_TO_TAKE = "Что взять?"
CHANGE_DATA = "Изменить данные"

main_menu_keyboard = ReplyKeyboardMarkup(
    [
        [ABOUT_TRIP, WHAT_TO_TAKE],
        [CHANGE_DATA]
    ],
    one_time_keyboard=True
)

ask_phone_number_keyboard = ReplyKeyboardMarkup(
    [[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]],
    one_time_keyboard=True
)

change_data_keyboard = ReplyKeyboardMarkup(
    [
        ["Имя", "Фамилию"],
        ["Отчество", "Группу"],
        ["Номер телефона", "Ожидания"],
        ["Особенности питания", "Назад"]
    ],
    one_time_keyboard=True
)

def next_step_keyboard(field_name):
    if field_name == "group":
        return ask_phone_number_keyboard
    return ReplyKeyboardMarkup([["Далее"]], one_time_keyboard=True)
