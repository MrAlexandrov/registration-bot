import pytest
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, Chat, Contact
from telegram.ext import CallbackContext
from registration_handler import RegistrationFlow
from user_storage import user_storage


@pytest.fixture(autouse=True)
def reset_user_storage():
    """Очищает базу данных перед каждым тестом."""
    user_storage.cursor.execute("DELETE FROM users")
    user_storage.conn.commit()


@pytest.fixture
def registration_flow():
    """Создает экземпляр класса RegistrationFlow."""
    return RegistrationFlow(user_storage)


@pytest.fixture
def mock_user():
    """Создает мокового пользователя."""
    return User(id=500261451, first_name="TestUser", is_bot=False)


@pytest.fixture
def mock_chat():
    """Создает моковый чат."""
    return Chat(id=500261451, type="private")


@pytest.fixture
def mock_context():
    """Создает моковый CallbackContext."""
    context = AsyncMock(spec=CallbackContext)
    context.bot.send_message = AsyncMock()  # Делаем send_message асинхронным
    return context


def create_mock_message(chat, user, text=None, contact=None):
    """Создает новый объект Message вместо изменения текста в mock_update."""
    return Message(
        message_id=1,
        date=None,
        chat=chat,
        from_user=user,
        text=text,
        contact=contact,
    )


@pytest.mark.asyncio
async def test_start_command(registration_flow, mock_user, mock_chat, mock_context):
    """Тест команды /start"""
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, text="/start")

    await registration_flow.handle_command(mock_update, mock_context)

    user = user_storage.get_user(mock_user.id)
    assert user is not None
    assert user["state"] == "name"
    mock_context.bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_registration_flow(registration_flow, mock_user, mock_chat, mock_context):
    """Тест полного процесса регистрации"""
    user_id = mock_user.id
    user_storage.create_user(user_id)

    # Ввод имени
    user_storage.update_state(user_id, "name")
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, text="Иван")

    await registration_flow.handle_input(mock_update, mock_context)
    assert user_storage.get_user(user_id)["name"] == "Иван"

    # Ввод телефона
    user_storage.update_state(user_id, "phone")
    mock_update.message = create_mock_message(mock_chat, mock_user, text="71234567890")

    await registration_flow.handle_input(mock_update, mock_context)
    assert user_storage.get_user(user_id)["phone"] == "71234567890"

    # Ввод email
    user_storage.update_state(user_id, "email")
    mock_update.message = create_mock_message(mock_chat, mock_user, text="test@example.com")

    await registration_flow.handle_input(mock_update, mock_context)
    assert user_storage.get_user(user_id)["email"] == "test@example.com"

    # Ввод возраста
    user_storage.update_state(user_id, "birth_date")
    mock_update.message = create_mock_message(mock_chat, mock_user, text="10.03.2002")

    await registration_flow.handle_input(mock_update, mock_context)
    assert user_storage.get_user(user_id)["birth_date"] == "10.03.2002"

    assert user_storage.get_user(user_id)["state"] == "registered"


@pytest.mark.asyncio
async def test_editing_data(registration_flow, mock_user, mock_chat, mock_context):
    """Тест редактирования данных"""
    user_id = mock_user.id
    user_storage.create_user(user_id)
    user_storage.update_state(user_id, "registered")

    # Выбор редактирования
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, text="Изменить данные")

    await registration_flow.handle_input(mock_update, mock_context)
    assert user_storage.get_user(user_id)["state"] == "edit"

    # Выбор редактирования имени
    mock_update.message = create_mock_message(mock_chat, mock_user, text="Имя")

    await registration_flow.handle_input(mock_update, mock_context)
    assert user_storage.get_user(user_id)["state"] == "edit_name"

    # Ввод нового имени
    mock_update.message = create_mock_message(mock_chat, mock_user, text="Алексей")

    await registration_flow.handle_input(mock_update, mock_context)
    assert user_storage.get_user(user_id)["name"] == "Алексей"
    assert user_storage.get_user(user_id)["state"] == "registered"


@pytest.mark.asyncio
async def test_phone_sharing(registration_flow, mock_user, mock_chat, mock_context):
    """Тест кнопки 'Поделиться номером'"""
    user_id = mock_user.id
    user_storage.create_user(user_id)
    user_storage.update_state(user_id, "phone")

    contact = Contact(phone_number="79998887766", user_id=user_id, first_name="TestUser")
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, contact=contact)

    await registration_flow.handle_input(mock_update, mock_context)

    assert user_storage.get_user(user_id)["phone"] == "79998887766"
    assert user_storage.get_user(user_id)["state"] == "email"


@pytest.mark.asyncio
async def test_invalid_email_input(registration_flow, mock_user, mock_chat, mock_context):
    """Тест обработки неверного email"""
    user_id = mock_user.id
    user_storage.create_user(user_id)
    user_storage.update_state(user_id, "email")

    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, text="invalid-email")

    await registration_flow.handle_input(mock_update, mock_context)

    assert user_storage.get_user(user_id)["state"] == "email"  # Состояние не изменилось
