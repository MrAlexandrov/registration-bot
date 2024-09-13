import pytest
from unittest.mock import AsyncMock
from telegram import ReplyKeyboardMarkup, KeyboardButton
from main import start, handle_message

@pytest.mark.asyncio
async def test_start_command(mock_update, mocker):
    # Создаем mock-объект Update с кастомными параметрами
    mock_update_instance = mock_update(user_id=987654321, first_name="Павел", last_name="Иванов")
    
    # Мокаем контекст
    mock_context = AsyncMock()

    # Тестируем команду /start
    await start(mock_update_instance, mock_context)

    # Проверяем, что было отправлено корректное сообщение с клавиатурой
    expected_keyboard = ReplyKeyboardMarkup(
        [[KeyboardButton(text='Да'), KeyboardButton(text='Нет, исправить')]],
        resize_keyboard=True
    )
    
    mock_update_instance.message.reply_text.assert_called_once_with(
        "Привет! Я бот для регистрации на Пионерский выезд 2024. Давай знакомиться, тебя зовут Павел?",
        reply_markup=expected_keyboard
    )
