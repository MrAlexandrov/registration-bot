from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, filters

from user_storage import UserStorage

class RegistrationFlow:
    def __init__(self):
        self.user_storage = UserStorage()
        self.steps = ["name", "phone", "email", "age"]

    async def start_registration(self, update: Update, context: CallbackContext):
        """Запускает регистрацию с первого шага."""
        user_id = update.message.from_user.id
        user_data = self.user_storage.get_user(user_id)

        if not user_data:
            print(f"[DEBUG] Creating new user {user_id}")
            self.user_storage.create_user(user_id)
            await self.ask_question(update, context, "name")
        else:
            current_step = user_data["state"]
            if current_step == "registered":
                await update.message.reply_text("Вы уже зарегистрированы! ✅")
            else:
                await self.ask_question(update, context, current_step)

    async def handle_response(self, update: Update, context: CallbackContext):
        """Обрабатывает ответ пользователя и переходит к следующему шагу."""
        user_id = update.message.from_user.id
        user_data = self.user_storage.get_user(user_id)

        if not user_data:
            await update.message.reply_text("❌ Что-то пошло не так! Попробуйте /start")
            return

        current_step = user_data["state"]
        if current_step == "registered":
            await update.message.reply_text("Вы уже зарегистрированы! ✅")
            return

        # Сохраняем ответ пользователя
        self.user_storage.update_user(user_id, current_step, update.message.text)

        # Переход к следующему шагу
        next_step_index = self.steps.index(current_step) + 1
        if next_step_index < len(self.steps):
            next_step = self.steps[next_step_index]
            self.user_storage.update_state(user_id, next_step)
            await self.ask_question(update, context, next_step)
        else:
            # Регистрация завершена
            self.user_storage.update_state(user_id, "registered")
            await update.message.reply_text("✅ Регистрация завершена! Спасибо!")

    async def ask_question(self, update: Update, context: CallbackContext, step_name: str):
        """Отправляет вопрос пользователю в зависимости от текущего этапа."""
        questions = {
            "name": "Как вас зовут?",
            "phone": "Введите ваш телефон:",
            "email": "Введите ваш email:",
            "age": "Введите ваш возраст:"
        }

        if step_name in questions:
            await update.message.reply_text(questions[step_name])


# Инициализируем регистрацию
registration_flow = RegistrationFlow()
