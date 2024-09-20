import json
from pprint import pprint
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from settings import BOT_TOKEN, SPREADSHEET_ID, GOOGLE_CREDENTIALS_FILE, FIELDNAMES
from bot_logging import logger
from state_manager import get_user_state, set_user_state, load_scenario
from storage import UserStorage
from user import User

# Загрузка сценария
scenario = load_scenario()

# Хранилище пользователей
users = {}
storage = UserStorage()

# Универсальная функция для замены плейсхолдеров в сообщении
def replace_placeholders(message, placeholders):
    for placeholder, value in placeholders.items():
        message = message.replace(f"{{{placeholder}}}", str(value))
    return message

# Функция для отправки сообщений
async def send_message(update, message, buttons=None):
    if buttons:
        keyboard = ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())

# Обработка сервисных состояний
async def handle_service_state(state, user_id):
    if state == "check_double_registration":
        # Проверка, зарегистрирован ли пользователь
        if user_id in [user[0] for user in storage.get_all_users()]:
            return "message_already_registered"
        else:
            return "message_fill_first_name_first_time"
    elif state.startswith("save"):
        # Пример: сохранение данных
        if state == "save_first_name":
            # Логика сохранения имени
            storage.save_user(user_id, users[user_id])
        elif state == "save_last_name":
            # Логика сохранения фамилии
            storage.save_user(user_id, users[user_id])
        elif state == "save_group":
            # Логика сохранения группы
            storage.save_user(user_id, users[user_id])

    # Возвращаем следующее состояние
    return scenario[state]["next_state"]

# Обработка кнопок
def handle_button_response(update, next_state_dict):
    user_input = update.message.text
    logger.info(f"Обработка кнопочного ввода: {user_input}")

    # Найти соответствующее состояние на основе введённого текста
    if user_input in next_state_dict:
        return next_state_dict[user_input]
    else:
        return "invalid_input"

# Обработка ввода
async def handle_input_state(update, state):
    user_input = update.message.text
    user_id = update.message.from_user.id

    if state == "fill_first_name_first_time":
        users[user_id]['first_name'] = user_input
    elif state == "fill_last_name_first_time":
        users[user_id]['last_name'] = user_input
    elif state == "fill_group_first_time":
        users[user_id]['group'] = user_input
    # ... другие состояния ввода
    return scenario[state]["next_state"]

# Универсальный обработчик состояний
async def handle_state(update, context):
    user_id = update.message.from_user.id
    state = get_user_state(user_id)

    # Проверка на существование состояния в сценарии
    if state not in scenario:
        logger.error(f"Состояние '{state}' не найдено в сценарии")
        await update.message.reply_text(f"Ошибка: состояние '{state}' не найдено в сценарии.")
        return

    logger.info(f"Текущее состояние: {state}, Тип состояния: {scenario[state]['type']}")
    state_data = scenario[state]
    state_type = state_data["type"]

    if state_type == "message":
        # Обработка вывода сообщения
        message = replace_placeholders(state_data["message"], users.get(user_id, {}))
        buttons = state_data.get("buttons")
        await send_message(update, message, buttons)
        next_state = state_data["next_state"]

    elif state_type == "service":
        # Обработка сервисного состояния
        next_state = await handle_service_state(state, user_id)

    elif state_type == "button":
        # Обработка выбора кнопок
        buttons = list(state_data["next_state"].keys())
        await send_message(update, state_data.get("message", "Пожалуйста, используйте кнопки."), buttons)

        next_state = handle_button_response(update, state_data["next_state"])
        if next_state == "invalid_input":
            await update.message.reply_text("Пожалуйста, используйте кнопки.")
            return  # Остаёмся в текущем состоянии

    elif state_type == "input":
        # Обработка текстового ввода пользователя
        next_state = await handle_input_state(update, state)

    # Обновляем состояние пользователя
    set_user_state(user_id, next_state)

    # Переходим к следующему состоянию
    if next_state in scenario:
        await handle_state(update, context)

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    users[user_id] = {
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'group': None,
        'username': update.message.from_user.username
    }
    # Начинаем процесс
    set_user_state(user_id, "start")
    await handle_state(update, context)


if __name__ == '__main__':
    test = User(123, "first_name", "second_name", "group", "username")
    google_storage = GoogleSheetsStorage(credentials_file=GOOGLE_CREDENTIALS_FILE, spreadsheet_id=SPREADSHEET_ID)
    csv_storage = CSVFileStorage()

    google_storage.save_user(test)
    csv_storage.save_user(test)
    google_storage.save_user(test)
    csv_storage.save_user(test)
    pprint(google_storage.get_all_users())
    pprint(csv_storage.get_all_users())
    # app = ApplicationBuilder().token(BOT_TOKEN).build()

    # app.add_handler(CommandHandler("start", start))
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_state))

    # logger.info("Запуск бота...")
    # app.run_polling()
