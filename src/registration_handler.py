from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import CallbackContext
from user_storage import user_storage
from settings import FIELDS, POST_REGISTRATION_STATES


class RegistrationFlow:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.steps = [field["name"] for field in FIELDS]

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
        """Общий метод перехода между состояниями."""
        user_id = update.message.from_user.id
        print(f"[DEBUG] Переход к состоянию '{state}' для пользователя {user_id}")

        if state in POST_REGISTRATION_STATES:
            await self.handle_post_registration_state(update, context, state)
        else:
            await self.handle_registration_state(update, context, state)

    async def handle_registration_state(self, update, context, state):
        """Обрабатывает состояния, связанные с регистрацией."""
        user_id = update.message.from_user.id
        field_config = next((f for f in FIELDS if f["name"] == state), None)

        if not field_config:
            print(f"[ERROR] Состояние '{state}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        print(f"[DEBUG] Задаём вопрос '{field_config['question']}' для пользователя {user_id}")
        self.user_storage.update_state(user_id, state)

        reply_markup = (
            ReplyKeyboardMarkup(
                [[KeyboardButton(text="Поделиться номером", request_contact=True)]],
                resize_keyboard=True
            ) if field_config.get("request_contact") else ReplyKeyboardRemove()
        )

        await context.bot.send_message(chat_id=user_id, text=field_config["question"], reply_markup=reply_markup)

    async def handle_post_registration_state(self, update, context, state):
        """Обрабатывает состояния после регистрации (например, редактирование)."""
        user_id = update.message.from_user.id
        config = POST_REGISTRATION_STATES[state]
        print(f"[DEBUG] Пользователь {user_id} переходит в состояние '{state}' после регистрации.")
        self.user_storage.update_state(user_id, state)

        if state == "registered":
            user = self.user_storage.get_user(user_id)
            message = config["message"].format(
                name=user.get("name", "Не указано"),
                phone=user.get("phone", "Не указано"),
                email=user.get("email", "Не указано"),
                age=user.get("age", "Не указано")
            )
        else:
            message = config["message"]

        buttons = config.get("buttons")
        if callable(buttons):  
            buttons = buttons()

        reply_markup = ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True) if buttons else ReplyKeyboardRemove()

        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup)

    async def handle_input(self, update, context):
        """Обрабатывает пользовательский ввод."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)
        current_state = user["state"]
        print(f"[DEBUG] Пользователь {user_id} находится в состоянии '{current_state}'")

        if current_state == "registered":
            await self.process_registered_input(update, context)
        elif current_state == "edit":
            await self.process_edit_input(update, context)
        elif current_state.startswith("edit_") or current_state in self.steps:
            await self.process_field_input(update, context, current_state)
        else:
            print(f"[ERROR] Некорректное текущее состояние '{current_state}' для пользователя {user_id}.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")

    async def process_field_input(self, update, context, current_state):
        """Обрабатывает ввод данных в процессе регистрации и редактирования."""
        user_id = update.message.from_user.id
        field_name = current_state.replace("edit_", "")
        field_config = next((f for f in FIELDS if f["name"] == field_name), None)

        if not field_config:
            print(f"[ERROR] Поле '{field_name}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        user_input = update.message.contact.phone_number if update.message.contact else update.message.text

        if "validator" in field_config and not field_config["validator"](user_input):
            print(f"[DEBUG] Некорректное значение '{user_input}' для поля '{field_name}'")
            await context.bot.send_message(chat_id=user_id, text=f"Некорректное значение для {field_config['label']}. Попробуй снова.")
            return

        formatted_value = field_config["formatter"](user_input) if "formatter" in field_config and callable(field_config["formatter"]) else user_input
        self.user_storage.update_user(user_id, field_name, formatted_value)
        print(f"[DEBUG] Сохранён ответ '{formatted_value}' для поля '{field_name}'")

        next_state = "registered" if current_state.startswith("edit_") else (
            self.steps[self.steps.index(current_state) + 1] if current_state != self.steps[-1] else "registered"
        )

        await self.transition_state(update, context, next_state)

    async def process_registered_input(self, update, context):
        """Обрабатывает ввод в состоянии 'registered'."""
        user_id = update.message.from_user.id
        user_input = update.message.text

        if user_input == "Изменить данные":
            print(f"[DEBUG] Пользователь {user_id} выбрал 'Изменить данные'.")
            await self.transition_state(update, context, "edit")
        else:
            print(f"[ERROR] Некорректный ввод '{user_input}' в состоянии 'registered'.")
            await context.bot.send_message(chat_id=user_id, text="Пожалуйста, выбери действие из предложенных.")

    async def process_edit_input(self, update, context):
        """Обрабатывает выбор поля для редактирования."""
        user_id = update.message.from_user.id
        field_label = update.message.text

        if field_label == "Отмена":
            print(f"[DEBUG] Пользователь {user_id} отменил редактирование.")
            await self.transition_state(update, context, "registered")
            return

        field_config = next((f for f in FIELDS if f["label"] == field_label), None)
        if not field_config:
            print(f"[ERROR] Поле с меткой '{field_label}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        next_state = f"edit_{field_config['name']}"
        print(f"[DEBUG] Переход к состоянию '{next_state}' для пользователя {user_id}")
        await self.transition_state(update, context, next_state)

# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
