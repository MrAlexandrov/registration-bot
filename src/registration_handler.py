from settings import FIELDS
from telegram import Update
from telegram.ext import CallbackContext
from user_storage import user_storage
from utils import normalize_phone

class RegistrationFlow:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.steps = [field["name"] for field in FIELDS]

    async def start_registration(self, update, context):
        """Начинает процесс регистрации."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)

        if not user:
            print(f"[DEBUG] Создание нового пользователя {user_id}")
            self.user_storage.create_user(user_id, self.steps[0])
            user = self.user_storage.get_user(user_id)

        if user and user["state"] == "registered":
            await context.bot.send_message(chat_id=user_id, text="✅ Вы уже зарегистрированы!")
            return

        current_state = user["state"]
        print(f"[DEBUG] Текущее состояние пользователя {user_id}: {current_state}")
        if current_state not in self.steps:
            current_state = self.steps[0]

        await self.ask_question(update, context, current_state)

    async def handle_registration_step(self, update, context):
        """Обрабатывает ввод пользователя на текущем шаге."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)

        if not user:
            await context.bot.send_message(chat_id=user_id, text="Пожалуйста, начните с команды /start.")
            return

        current_state = user["state"]
        print(f"[DEBUG] Выполняется шаг '{current_state}' для пользователя {user_id}")

        # Найти текущий шаг и его валидатор
        field = next((field for field in FIELDS if field["name"] == current_state), None)
        if not field:
            await context.bot.send_message(chat_id=user_id, text="Ошибка: не могу найти шаг регистрации.")
            return

        validator = field.get("validator")

        # Проверить данные
        if validator and not validator(update.message.text):
            await context.bot.send_message(chat_id=user_id, text="Данные введены некорректно. Попробуйте ещё раз.")
            await self.ask_question(update, context, current_state)
            return

        step_name = field.get("name")

        # Сохранить данные, если валидатор прошёл
        if step_name == "phone":
            normalized_value = normalize_phone(update.message.text)
            if not normalized_value:
                await context.bot.send_message(chat_id=user_id, text="Введите корректный номер телефона.")
                return
            self.user_storage.update_user(user_id, step_name, normalized_value)
        else:
            self.user_storage.update_user(user_id, step_name, update.message.text)

        print(f"[DEBUG] Сохранён ответ '{update.message.text}' для шага '{current_state}'")

        # Переход к следующему шагу
        next_step_index = self.steps.index(current_state) + 1
        if next_step_index < len(self.steps):
            next_step_name = self.steps[next_step_index]
            self.user_storage.update_state(user_id, next_step_name)
            await self.ask_question(update, context, next_step_name)
        else:
            print(f"[DEBUG] Регистрация завершена для пользователя {user_id}")
            await context.bot.send_message(chat_id=user_id, text="✅ Регистрация завершена!")
            self.user_storage.update_state(user_id, "registered")

    async def ask_question(self, update, context, step_name):
        """Задаёт вопрос для текущего шага."""
        user_id = update.message.from_user.id
        question = next(field["question"] for field in FIELDS if field["name"] == step_name)
        print(f"[DEBUG] Задаём вопрос '{question}' для пользователя {user_id}")
        await context.bot.send_message(chat_id=user_id, text=question)

# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
