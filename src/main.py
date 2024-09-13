import json
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from settings import BOT_TOKEN
from bot_logging import logger
from storage import FileStorage
from state_manager import get_user_state, set_user_state, load_scenario

# Хранилище пользователей
users = {}

# Создаем экземпляр класса для хранения данных в файле
storage = FileStorage()

# Загрузка сценария
scenario = load_scenario()

# Универсальная функция для замены плейсхолдеров в сообщении
def replace_placeholders(message, placeholders):
    """Заменяет плейсхолдеры в сообщении на значения из переданного словаря."""
    for placeholder, value in placeholders.items():
        message = message.replace(f"{{{placeholder}}}", str(value))
    return message

# Функция для отправки сообщений с клавиатурой или без
async def send_message(update: Update, message: str, buttons: list = None):
    """Отправляет сообщение пользователю. Если указаны кнопки, добавляет их."""
    if buttons:
        keyboard = ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True)
        await update.message.reply_text(message, reply_markup=keyboard)
    else:
        await update.message.reply_text(message, reply_markup=ReplyKeyboardRemove())

# Универсальная функция для обработки переходов на основе кнопок
def handle_button_response(user_input: str, next_state_dict: dict):
    """Обрабатывает пользовательский ввод и возвращает соответствующее состояние на основе кнопок."""
    for button, state in next_state_dict.items():
        if user_input.lower() == button.lower():
            return state
    return 'invalid_input'

# Обработчик команды /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id

    # Сохраняем данные пользователя (имя и фамилию)
    users[user_id] = {
        'first_name': update.message.from_user.first_name,
        'last_name': update.message.from_user.last_name,
        'group': None
    }

    # Устанавливаем начальное состояние
    set_user_state(user_id, "start")
    state = get_user_state(user_id)

    # Заменяем плейсхолдеры в сообщении
    message = replace_placeholders(scenario['states'][state]['message'], users[user_id])

    # Получаем кнопки из сценария
    buttons = scenario['states'][state].get('buttons')

    # Отправляем сообщение с кнопками, если они есть
    await send_message(update, message, buttons)

# Обработка состояний
async def process_state(update: Update, user_data: dict, state: str):
    user_id = update.message.from_user.id
    state_data = scenario['states'][state]
    next_state = state_data.get('next_state')

    # Если есть кнопки для выбора, обрабатываем их
    if isinstance(next_state, dict):
        next_state = handle_button_response(update.message.text, next_state)
        if next_state == 'invalid_input':
            await update.message.reply_text("Пожалуйста, выберите вариант с помощью кнопок.")
            return state  # Остаёмся в текущем состоянии

    # Если нужно сохранить данные пользователя
    if state == "waiting_for_name":
        user_data['first_name'] = update.message.text
    elif state == "waiting_for_surname":
        user_data['last_name'] = update.message.text
    elif state == "waiting_for_group":
        user_data['group'] = update.message.text

    return next_state

# Универсальный обработчик для работы с состояниями
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    state = get_user_state(user_id)
    user_data = users.get(user_id, {})

    # Обработка текущего состояния и получение следующего состояния
    next_state = await process_state(update, user_data, state)

    # Обновляем состояние пользователя
    set_user_state(user_id, next_state)

    # Заменяем плейсхолдеры на данные пользователя
    message = replace_placeholders(scenario['states'][next_state]['message'], user_data)

    # Получаем кнопки из сценария
    buttons = scenario['states'][next_state].get('buttons')

    # Отправляем сообщение следующего состояния
    await send_message(update, message, buttons)


if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Запуск бота...")
    app.run_polling()
