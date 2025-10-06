import pytest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock
from telegram import Update, User, Message, Chat, Contact
from telegram.ext import CallbackContext


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary test database for each test."""
    # Create a temporary database file
    fd, db_path = tempfile.mkstemp(suffix='.sqlite')
    os.close(fd)

    # Import and initialize with test database
    from src.user_storage import UserStorage
    test_storage = UserStorage(db_path)

    yield test_storage

    # Cleanup
    try:
        os.unlink(db_path)
    except:
        pass


@pytest.fixture
def user_storage(test_db):
    """Provide user_storage for tests."""
    return test_db


@pytest.fixture
def registration_flow(user_storage):
    """Create RegistrationFlow with test user_storage."""
    from src.registration_handler import RegistrationFlow
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
    return MagicMock(spec=Message, chat=chat, from_user=user, text=text, contact=contact)


@pytest.mark.asyncio
async def test_start_command(registration_flow, mock_user, mock_chat, mock_context):
    """Тест команды /start"""
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, text="/start")
    mock_update.callback_query = None

    await registration_flow.handle_command(mock_update, mock_context)

    user = registration_flow.user_storage.get_user(mock_user.id)
    assert user is not None
    assert user["state"] == "username"
    mock_context.bot.send_message.assert_called_once()


@pytest.mark.asyncio
async def test_registration_flow(registration_flow, mock_user, mock_chat, mock_context):
    """Тест полного процесса регистрации"""
    user_id = mock_user.id
    registration_flow.user_storage.create_user(user_id)

    test_data = {
        "name": "Иван",
        "birth_date": "10.03.2002",
        "phone": "71234567890",
        "username": "testuser",
        "email": "test@example.com",
        "position": "Вожатый",
        "desired_age": "6-9",
        "probability_instructive": "0-25",
        "probability_first": "25-50",
        "probability_second": "50-75",
        "education_choice": "МГТУ им. Баумана",
        "study_group": "ИУ7-51",
        "work": "Да",
        "work_place": "Yandex",
        "diplom": "Да",
        "rescheduling_session": "Да",
        "rescheduling_practice": "Нет",
        "medical_book": "Да",
    }

    for field, value in test_data.items():
        registration_flow.user_storage.update_state(user_id, field)
        mock_update = MagicMock(spec=Update)
        mock_update.effective_user = mock_user
        mock_update.callback_query = None

        # For fields with options, we need to simulate an inline query
        if field in ["position", "desired_age", "probability_instructive", "probability_first", "probability_second", "education_choice", "work", "diplom", "rescheduling_session", "rescheduling_practice", "medical_book"]:
            # Step 1: Select an option
            mock_update.callback_query = AsyncMock()
            mock_update.callback_query.data = f"select|{value}"
            mock_update.callback_query.from_user = mock_user
            mock_update.callback_query.message = create_mock_message(mock_chat, mock_user, text=value)
            await registration_flow.handle_inline_query(mock_update, mock_context)

            # Step 2: Click "Done"
            mock_update.callback_query.data = "done"
            await registration_flow.handle_inline_query(mock_update, mock_context)
        else:
            mock_update.message = create_mock_message(mock_chat, mock_user, text=value)
            await registration_flow.handle_input(mock_update, mock_context)

        assert registration_flow.user_storage.get_user(user_id)[field] == value

    assert registration_flow.user_storage.get_user(user_id)["state"] == "registered"


@pytest.mark.asyncio
async def test_editing_data(registration_flow, mock_user, mock_chat, mock_context):
    """Тест редактирования данных"""
    user_id = mock_user.id
    registration_flow.user_storage.create_user(user_id)
    registration_flow.user_storage.update_state(user_id, "registered")

    # Выбор редактирования
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, text="Изменить данные")
    mock_update.callback_query = None

    await registration_flow.handle_input(mock_update, mock_context)
    assert registration_flow.user_storage.get_user(user_id)["state"] == "edit"

    # Выбор редактирования имени
    mock_update.message = create_mock_message(mock_chat, mock_user, text="Имя")
    mock_update.callback_query = None

    await registration_flow.handle_input(mock_update, mock_context)
    assert registration_flow.user_storage.get_user(user_id)["state"] == "edit_name"

    # Ввод нового имени
    mock_update.message = create_mock_message(mock_chat, mock_user, text="Алексей")
    mock_update.callback_query = None

    await registration_flow.handle_input(mock_update, mock_context)
    assert registration_flow.user_storage.get_user(user_id)["name"] == "Алексей"
    assert registration_flow.user_storage.get_user(user_id)["state"] == "registered"


@pytest.mark.asyncio
async def test_phone_sharing(registration_flow, mock_user, mock_chat, mock_context):
    """Тест кнопки 'Поделиться номером'"""
    user_id = mock_user.id
    registration_flow.user_storage.create_user(user_id)
    registration_flow.user_storage.update_state(user_id, "phone")

    contact = MagicMock(spec=Contact, phone_number="79998887766", user_id=user_id, first_name="TestUser")
    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, contact=contact)
    mock_update.callback_query = None

    await registration_flow.handle_input(mock_update, mock_context)

    assert registration_flow.user_storage.get_user(user_id)["phone"] == "79998887766"
    assert registration_flow.user_storage.get_user(user_id)["state"] == "email"


@pytest.mark.asyncio
async def test_invalid_email_input(registration_flow, mock_user, mock_chat, mock_context):
    """Тест обработки неверного email"""
    user_id = mock_user.id
    registration_flow.user_storage.create_user(user_id)
    registration_flow.user_storage.update_state(user_id, "email")

    mock_update = MagicMock(spec=Update)
    mock_update.effective_user = mock_user
    mock_update.message = create_mock_message(mock_chat, mock_user, text="invalid-email")

    await registration_flow.handle_input(mock_update, mock_context)

    assert registration_flow.user_storage.get_user(user_id)["state"] == "email"
    mock_context.bot.send_message.assert_called_with(
        chat_id=user_id, text="Неверный формат email. Пожалуйста, введите корректный email."
    )
