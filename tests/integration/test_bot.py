import pytest
import asyncio
from telegram import Update, Bot
from telegram.ext import Application
from unittest.mock import AsyncMock
from src.main import save_message, show_data  # Импортируем обработчики

@pytest.mark.asyncio
async def test_save_message():
    """Тестируем сохранение сообщения в контекст бота"""
    update = AsyncMock()
    update.message.text = "Hello, bot!"
    update.message.date.timestamp.return_value = 1234567890
    update.message.entities = []

    context = AsyncMock()
    context.chat_data = {}

    await save_message(update, context)

    assert "messages" in context.chat_data
    assert len(context.chat_data["messages"]) == 1
    assert context.chat_data["messages"][0]["message"] == "Hello, bot!"

@pytest.mark.asyncio
async def test_show_data():
    """Тестируем отображение истории сообщений"""
    update = AsyncMock()
    update.message.reply_text = AsyncMock()

    context = AsyncMock()
    context.chat_data = {
        "messages": [{"message": "Hello, bot!", "message_ts": 1234567890}]
    }

    await show_data(update, context)

    update.message.reply_text.assert_called_once()
    called_args = update.message.reply_text.call_args[0][0]
    assert "Hello, bot!" in called_args
