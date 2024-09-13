import sys
import os

import pytest
from unittest.mock import Mock
from telegram import Update, Message, User, Chat

# Добавляем папку src в PYTHONPATH для тестов
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

@pytest.fixture
def mock_update(mocker):
    """Универсальная фикстура для создания mock-объекта Update с параметрами."""
    def _create_mock_update(user_id=123456789, first_name="Александр", last_name="Смирнов", text="/start"):
        mock_update = mocker.Mock(spec=Update)
        mock_update.message = mocker.Mock(spec=Message)
        mock_update.message.from_user = mocker.Mock(spec=User)
        mock_update.message.from_user.first_name = first_name
        mock_update.message.from_user.last_name = last_name
        mock_update.message.chat = mocker.Mock(spec=Chat)
        mock_update.message.chat.id = user_id
        mock_update.message.text = text
        return mock_update
    return _create_mock_update