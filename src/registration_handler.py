from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from user_storage import user_storage
from settings import FIELDS, POST_REGISTRATION_STATES
from telegram.constants import ParseMode

class RegistrationFlow:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.steps = [field["name"] for field in FIELDS]
        self.states_config = {state["name"]: state for state in POST_REGISTRATION_STATES}

    async def handle_command(self, update, context):
        """Обрабатывает команды, такие как /start."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)

        if not user:
            print(f"[DEBUG] Создание нового пользователя {user_id}")
            self.user_storage.create_user(user_id)
            await self.transition_state(update, context, self.steps[0])
        else:
            print(f"[DEBUG] Пользователь {user_id} уже существует в состоянии '{user['state']}'")
            await self.transition_state(update, context, user["state"])

    async def transition_state(self, update, context, state):
        """Общий метод перехода между состояниями (регистрация и редактирование)."""
        user_id = update.message.from_user.id
        print(f"[DEBUG] Переход к состоянию '{state}' для пользователя {user_id}")

        config = self.get_config_by_name(state)
        if not config:
            print(f"[ERROR] Состояние '{state}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        self.user_storage.update_state(user_id, state)
        message = self.get_state_message(config, user_id)
        print(f"message = {message}")
        reply_markup = self.create_reply_markup(config)

        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    async def handle_input(self, update, context):
        """Обрабатывает пользовательский ввод для всех состояний."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)
        current_state = user["state"]

        print(f"[DEBUG] Пользователь {user_id} находится в состоянии '{current_state}'")

        config = self.get_config_by_name(current_state)
        if not config:
            print(f"[ERROR] Некорректное состояние '{current_state}'")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        user_input = update.message.contact.phone_number if update.message.contact else update.message.text

        # Обработка выбора действия (edit, registered)
        if "buttons" in config:
            await self.process_action_input(update, context, user_input, current_state)
            return

        # Обработка ввода данных (регистрация/редактирование)
        await self.process_data_input(update, context, user_input, current_state)

    async def process_action_input(self, update, context, user_input, current_state):
        """Обрабатывает кнопки в состояниях registered и edit."""
        user_id = update.message.from_user.id
        if current_state == "registered" and user_input == "Изменить данные":
            print(f"[DEBUG] Пользователь {user_id} выбрал 'Изменить данные'.")
            await self.transition_state(update, context, "edit")
            return

        if current_state == "edit":
            if user_input == "Отмена":
                print(f"[DEBUG] Пользователь {user_id} отменил редактирование.")
                await self.transition_state(update, context, "registered")
                return

            field_config = self.get_config_by_label(user_input)
            if not field_config:
                print(f"[ERROR] Поле '{user_input}' не найдено.")
                await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
                return

            await self.transition_state(update, context, f"edit_{field_config['name']}")

    async def process_data_input(self, update, context, user_input, current_state):
        """Обрабатывает ввод данных (включая валидацию и форматирование)."""
        user_id = update.message.from_user.id
        field_name = current_state.replace("edit_", "")
        field_config = self.get_config_by_name(field_name)

        if not field_config:
            print(f"[ERROR] Поле '{field_name}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        if "validator" in field_config and not field_config["validator"](user_input):
            print(f"[DEBUG] Некорректное значение '{user_input}' для поля '{field_name}'")
            await context.bot.send_message(chat_id=user_id, text=f"Некорректное значение для {field_config['label']}. Попробуй снова.")
            return

        formatted_value = self.format_input(field_config, user_input)
        self.user_storage.update_user(user_id, field_name, formatted_value)
        print(f"[DEBUG] Сохранён ответ '{formatted_value}' для поля '{field_name}'")

        await self.transition_state(update, context, self.get_next_state(current_state))

    def get_next_state(self, current_state):
        """Определяет следующее состояние."""
        if current_state.startswith("edit_"):
            return "registered"
        elif current_state in self.steps and current_state != self.steps[-1]:
            return self.steps[self.steps.index(current_state) + 1]
        else:
            return "registered"

    def get_config_by_name(self, state_name):
        """Возвращает конфигурацию состояния по имени."""
        return next((f for f in FIELDS if f["name"] == state_name), None) or self.states_config.get(state_name)

    def get_config_by_label(self, label):
        """Возвращает конфигурацию поля по его label (используется в редактировании)."""
        return next((f for f in FIELDS if f["label"] == label), None)

    def format_input(self, field_config, user_input):
        """Форматирует данные, если у поля есть форматтер."""
        return field_config["formatter"](user_input) if "formatter" in field_config and callable(field_config["formatter"]) else user_input

    def get_state_message(self, config, user_id):
        """Формирует сообщение состояния, включая подстановку данных пользователя с форматированием Markdown."""
        if config["name"] == "registered":
            user = self.user_storage.get_user(user_id)

            # Формируем словарь для подстановки значений
            user_data = {field["name"]: f"`{user.get(field['name'], 'Не указано')}`" for field in FIELDS}

            # Создаём динамическое сообщение с разметкой Markdown
            message = "*Отлично! Вот, что я запомнил:*\n"
            message += "\n".join([f"*{field['label']}*: {{{field['name']}}}" for field in FIELDS])

            # Подставляем данные
            return message.format(**user_data)

        return config["message"]


    def create_reply_markup(self, config):
        """Создает клавиатуру для состояния."""
        if "buttons" in config:
            buttons = self.create_buttons(config)
            return ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True) if buttons else ReplyKeyboardRemove()

        if config.get("request_contact"):
            return ReplyKeyboardMarkup([[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]], resize_keyboard=True)

        return ReplyKeyboardRemove()

    def create_buttons(self, config):
        """Создает список кнопок."""
        buttons = config.get("buttons")
        return buttons() if callable(buttons) else buttons


# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
