"""
Unit tests for message logger functionality.
"""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest

from src.message_logger import MessageLogger
from src.models import Message


class TestMessageLogger:
    """Test cases for MessageLogger class."""

    @pytest.fixture
    def message_logger(self):
        """Create a MessageLogger instance for testing."""
        return MessageLogger()

    @pytest.fixture
    def mock_update(self):
        """Create a mock Telegram Update object."""
        update = Mock()
        update.message = Mock()
        update.message.from_user = Mock()
        update.message.from_user.id = 12345
        update.message.chat_id = 12345
        update.message.message_id = 67890
        update.message.text = "Test message"
        update.message.caption = None
        update.message.photo = None
        update.message.document = None
        update.message.video = None
        update.message.audio = None
        update.message.voice = None
        update.message.sticker = None
        update.message.reply_to_message = None
        update.callback_query = None
        return update

    @pytest.fixture
    def mock_sent_message(self):
        """Create a mock sent Telegram Message object."""
        message = Mock()
        message.message_id = 99999
        message.text = "Bot response"
        message.caption = None
        message.photo = None
        message.document = None
        message.video = None
        return message

    def test_get_message_type_text(self, message_logger, mock_update):
        """Test message type detection for text messages."""
        message_type = message_logger._get_message_type(mock_update.message)
        assert message_type == "text"

    def test_get_message_type_photo(self, message_logger, mock_update):
        """Test message type detection for photo messages."""
        mock_update.message.text = None
        mock_update.message.photo = [Mock()]
        message_type = message_logger._get_message_type(mock_update.message)
        assert message_type == "photo"

    def test_get_message_type_document(self, message_logger, mock_update):
        """Test message type detection for document messages."""
        mock_update.message.text = None
        mock_update.message.document = Mock()
        message_type = message_logger._get_message_type(mock_update.message)
        assert message_type == "document"

    def test_get_message_type_contact(self, message_logger, mock_update):
        """Test message type detection for contact messages."""
        mock_update.message.text = None
        mock_update.message.contact = Mock()
        message_type = message_logger._get_message_type(mock_update.message)
        assert message_type == "contact"


class TestMessageModel:
    """Test cases for Message model."""

    def test_message_model_creation(self):
        """Test creating a Message instance."""
        msg = Message(
            telegram_id=12345,
            chat_id=12345,
            message_id=67890,
            direction="incoming",
            message_type="text",
            text="Test message",
            created_at=datetime.now(UTC),
        )

        assert msg.telegram_id == 12345
        assert msg.chat_id == 12345
        assert msg.message_id == 67890
        assert msg.direction == "incoming"
        assert msg.message_type == "text"
        assert msg.text == "Test message"

    def test_message_model_repr(self):
        """Test Message __repr__ method."""
        msg = Message(
            telegram_id=12345,
            chat_id=12345,
            message_id=67890,
            direction="outgoing",
            message_type="text",
            text="Bot response",
            created_at=datetime.now(UTC),
        )

        repr_str = repr(msg)
        assert "Message" in repr_str
        assert "telegram_id=12345" in repr_str
        assert "direction='outgoing'" in repr_str
        assert "type='text'" in repr_str

    def test_message_model_to_dict(self):
        """Test Message to_dict method."""
        now = datetime.now(UTC)
        msg = Message(
            telegram_id=12345,
            chat_id=12345,
            message_id=67890,
            direction="incoming",
            message_type="text",
            text="Test message",
            created_at=now,
        )

        msg_dict = msg.to_dict()

        assert msg_dict["telegram_id"] == 12345
        assert msg_dict["chat_id"] == 12345
        assert msg_dict["message_id"] == 67890
        assert msg_dict["direction"] == "incoming"
        assert msg_dict["message_type"] == "text"
        assert msg_dict["text"] == "Test message"
        assert isinstance(msg_dict["created_at"], str)  # Should be ISO format string
