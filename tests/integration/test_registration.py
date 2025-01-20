import pytest
from telegram.ext import Application
from registration_handler import registration_flow
from user_storage import UserStorage
from settings import BOT_TOKEN

# Создаём тестовое хранилище пользователей
user_storage = UserStorage()

@pytest.mark.asyncio
async def test_registration_flow():
    """Тестирует полный процесс регистрации пользователя."""
    app = Application.builder().token(BOT_TOKEN).build()

    user_id = 12345678  # Тестовый user_id
    test_messages = ["Иван", "89991112233", "ivan@mail.com", "25"]  # Данные на ввод

    expected_data = {
        "telegram_id": user_id,
        "name": "Иван",
        "phone": "89991112233",
        "email": "ivan@mail.com",
        "age": "25",
        "state": "registered"
    }

    # Запускаем регистрацию
    await registration_flow.start_registration(FakeUpdate(user_id, "/start"), FakeContext(user_id))

    # Проходим все этапы регистрации
    for step, msg in zip(registration_flow.steps, test_messages):
        await registration_flow.handle_response(FakeUpdate(user_id, msg), FakeContext(user_id))

    # Проверяем, что все данные полностью соответствуют ожидаемым
    saved_user = user_storage.get_user(user_id)
    assert saved_user is not None, "❌ Ошибка: Пользователь не найден в БД!"

    for key, expected_value in expected_data.items():
        assert saved_user[key] == expected_value, f"❌ Ошибка: {key} не совпадает! Ожидалось {expected_value}, получили {saved_user[key]}"

    print("✅ Тест пройден: Регистрация работает корректно!")


### **Фейковые классы для тестов**
class FakeUpdate:
    """Фейковый объект Update."""
    def __init__(self, user_id, text):
        self.message = FakeMessage(user_id, text)

class FakeMessage:
    """Фейковое сообщение."""
    def __init__(self, user_id, text):
        self.chat_id = user_id  # Добавляем chat_id
        self.from_user = FakeUser(user_id)
        self.text = text

    async def reply_text(self, text):
        print(f"[FakeBot] Ответ бота: {text}")  # Симуляция ответа бота

class FakeUser:
    """Фейковый пользователь."""
    def __init__(self, user_id):
        self.id = user_id

class FakeBot:
    """Фейковый бот для тестов."""
    async def send_message(self, chat_id, text):
        print(f"[FakeBot] Отправлено пользователю {chat_id}: {text}")

class FakeContext:
    """Фейковый контекст."""
    def __init__(self, user_id):
        self.user_data = {}
        self.user_id = user_id
        self.bot = FakeBot()  # Добавляем фиктивного бота
