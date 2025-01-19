from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, CallbackContext, filters

class RegistrationFlow:
    """Гибкий класс для управления регистрацией пользователей."""

    # Определяем шаги регистрации
    STEPS = [
        {"name": "ask_name", "message": "Как тебя зовут?", "next": "ask_contact"},
        {"name": "ask_contact", "message": "Отправь свой номер телефона.", "next": None},
    ]

    def __init__(self):
        self.step_map = {step["name"]: step for step in self.STEPS}
        self.first_step = self.STEPS[0]["name"]

    def get_next_step(self, current_step):
        """Возвращает следующий шаг по имени текущего."""
        return self.step_map.get(current_step, {}).get("next")

    def get_message(self, step_name):
        """Возвращает сообщение для текущего шага."""
        return self.step_map.get(step_name, {}).get("message", "Ошибка: неизвестный шаг.")

    async def start_registration(self, update: Update, context: CallbackContext):
        """Запускаем процесс регистрации с первого шага."""
        return await self.run_step(update, context, self.first_step)

    async def run_step(self, update: Update, context: CallbackContext, step_name):
        """Выполняет указанный шаг регистрации."""
        next_step = self.get_next_step(step_name)

        # Сохраняем данные пользователя
        if step_name == "ask_name":
            context.user_data["name"] = update.message.text
        elif step_name == "ask_contact":
            context.user_data["phone"] = update.message.text

        # Если есть следующий шаг — переходим к нему
        if next_step:
            await update.message.reply_text(self.get_message(next_step))
            return next_step

        # Регистрация завершена
        name = context.user_data.get("name", "Неизвестно")
        phone = context.user_data.get("phone", "Неизвестно")
        await update.message.reply_text(f"🎉 Регистрация завершена!\n👤 Имя: {name}\n📞 Телефон: {phone}")
        return ConversationHandler.END

    async def cancel(self, update: Update, context: CallbackContext):
        """Отмена регистрации."""
        await update.message.reply_text("Регистрация отменена.")
        return ConversationHandler.END


registration_flow = RegistrationFlow()
