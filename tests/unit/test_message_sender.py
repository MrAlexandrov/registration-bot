"""
Unit tests for message sender functionality.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Bot
from telegram.error import Forbidden, NetworkError, RetryAfter

from src.message_sender import MessageSender


class TestMessageSender:
    """Test cases for MessageSender class."""

    @pytest.fixture
    def message_sender(self):
        """Create a MessageSender instance for testing."""
        return MessageSender(max_retries=3, retry_delay=0.1)

    @pytest.fixture
    def mock_bot(self):
        """Create a mock Telegram Bot instance."""
        return AsyncMock(spec=Bot)

    @pytest.fixture
    def mock_user_storage(self):
        """Create a mock user storage."""
        with patch("src.message_sender.user_storage") as mock:
            mock.get_user.return_value = None
            yield mock

    @pytest.fixture
    def mock_message_logger(self):
        """Create a mock message logger."""
        with patch("src.message_sender.message_logger") as mock:
            yield mock

    @pytest.mark.asyncio
    async def test_send_message_success(self, message_sender, mock_bot, mock_user_storage, mock_message_logger):
        """Test successful message sending."""
        chat_id = 12345
        text = "Test message"

        # Mock successful send_message
        mock_sent_message = Mock()
        mock_sent_message.message_id = 99999
        mock_bot.send_message.return_value = mock_sent_message

        # Call the method
        result = await message_sender.send_message(mock_bot, chat_id, text)

        # Assertions
        assert result is True
        mock_bot.send_message.assert_called_once_with(chat_id=chat_id, text=text)
        mock_message_logger.log_outgoing_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_user_blocked(self, message_sender, mock_bot, mock_user_storage, mock_message_logger):
        """Test message sending when user has blocked the bot."""
        chat_id = 12345
        text = "Test message"

        # Mock user as blocked
        mock_user_storage.get_user.return_value = {"is_blocked": 1}

        # Call the method
        result = await message_sender.send_message(mock_bot, chat_id, text)

        # Assertions
        assert result is False
        mock_bot.send_message.assert_not_called()
        mock_message_logger.log_outgoing_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_message_forbidden_error(self, message_sender, mock_bot, mock_user_storage, mock_message_logger):
        """Test message sending when user has blocked the bot (Forbidden error)."""
        chat_id = 12345
        text = "Test message"

        # Mock Forbidden error
        mock_bot.send_message.side_effect = Forbidden("Bot was blocked by the user")

        # Call the method
        result = await message_sender.send_message(mock_bot, chat_id, text)

        # Assertions
        assert result is False
        mock_bot.send_message.assert_called_once()
        mock_user_storage.update_user.assert_called_once_with(chat_id, "is_blocked", 1)
        mock_message_logger.log_outgoing_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_message_retry_after_error(
        self, message_sender, mock_bot, mock_user_storage, mock_message_logger
    ):
        """Test message sending with rate limiting (RetryAfter error)."""
        chat_id = 12345
        text = "Test message"

        # Mock RetryAfter error followed by success
        mock_sent_message = Mock()
        mock_sent_message.message_id = 99999
        mock_bot.send_message.side_effect = [
            RetryAfter(1),  # First call - rate limited
            mock_sent_message,  # Second call - success
        ]

        # Call the method
        result = await message_sender.send_message(mock_bot, chat_id, text)

        # Assertions
        assert result is True
        assert mock_bot.send_message.call_count == 2
        mock_message_logger.log_outgoing_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_network_error_retry(
        self, message_sender, mock_bot, mock_user_storage, mock_message_logger
    ):
        """Test message sending with network errors and retries."""
        chat_id = 12345
        text = "Test message"

        # Mock NetworkError followed by success
        mock_sent_message = Mock()
        mock_sent_message.message_id = 99999
        mock_bot.send_message.side_effect = [
            NetworkError("Network error"),  # First call - network error
            mock_sent_message,  # Second call - success
        ]

        # Call the method
        result = await message_sender.send_message(mock_bot, chat_id, text)

        # Assertions
        assert result is True
        assert mock_bot.send_message.call_count == 2
        mock_message_logger.log_outgoing_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_network_error_max_retries(
        self, message_sender, mock_bot, mock_user_storage, mock_message_logger
    ):
        """Test message sending with network errors reaching max retries."""
        chat_id = 12345
        text = "Test message"

        # Mock NetworkError for all retries
        mock_bot.send_message.side_effect = NetworkError("Network error")

        # Call the method
        result = await message_sender.send_message(mock_bot, chat_id, text)

        # Assertions
        assert result is False
        assert mock_bot.send_message.call_count == 3  # max_retries + 1
        mock_message_logger.log_outgoing_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_send_photo_success(self, message_sender, mock_bot, mock_user_storage, mock_message_logger):
        """Test successful photo sending."""
        chat_id = 12345
        photo = "photo_file_id"
        caption = "Test caption"

        # Mock successful send_photo
        mock_sent_message = Mock()
        mock_sent_message.message_id = 99999
        mock_bot.send_photo.return_value = mock_sent_message

        # Call the method
        result = await message_sender.send_photo(mock_bot, chat_id, photo, caption)

        # Assertions
        assert result is True
        mock_bot.send_photo.assert_called_once_with(chat_id=chat_id, photo=photo, caption=caption)
        mock_message_logger.log_outgoing_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_video_success(self, message_sender, mock_bot, mock_user_storage, mock_message_logger):
        """Test successful video sending."""
        chat_id = 12345
        video = "video_file_id"
        caption = "Test caption"

        # Mock successful send_video
        mock_sent_message = Mock()
        mock_sent_message.message_id = 99999
        mock_bot.send_video.return_value = mock_sent_message

        # Call the method
        result = await message_sender.send_video(mock_bot, chat_id, video, caption)

        # Assertions
        assert result is True
        mock_bot.send_video.assert_called_once_with(chat_id=chat_id, video=video, caption=caption)
        mock_message_logger.log_outgoing_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_document_success(self, message_sender, mock_bot, mock_user_storage, mock_message_logger):
        """Test successful document sending."""
        chat_id = 12345
        document = "document_file_id"
        caption = "Test caption"

        # Mock successful send_document
        mock_sent_message = Mock()
        mock_sent_message.message_id = 99999
        mock_bot.send_document.return_value = mock_sent_message

        # Call the method
        result = await message_sender.send_document(mock_bot, chat_id, document, caption)

        # Assertions
        assert result is True
        mock_bot.send_document.assert_called_once_with(chat_id=chat_id, document=document, caption=caption)
        mock_message_logger.log_outgoing_message.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_to_multiple_text(
        self, message_sender, mock_bot, mock_user_storage, mock_message_logger
    ):
        """Test sending text message to multiple users."""
        user_ids = [12345, 67890, 11111]
        text = "Test message"

        # Mock successful sends
        mock_sent_message = Mock()
        mock_sent_message.message_id = 99999
        message_sender.send_message = AsyncMock(return_value=True)

        # Call the method
        stats = await message_sender.send_message_to_multiple(mock_bot, user_ids, text, message_type="text")

        # Assertions
        assert stats == {"success": 3, "failed": 0}
        assert message_sender.send_message.call_count == 3

    @pytest.mark.asyncio
    async def test_send_message_to_multiple_photo(
        self, message_sender, mock_bot, mock_user_storage, mock_message_logger
    ):
        """Test sending photo to multiple users."""
        user_ids = [12345, 67890]
        caption = "Test caption"
        photo = "photo_file_id"

        # Mock successful sends
        message_sender.send_photo = AsyncMock(return_value=True)

        # Call the method
        stats = await message_sender.send_message_to_multiple(
            mock_bot, user_ids, caption, message_type="photo", photo=photo
        )

        # Assertions
        assert stats == {"success": 2, "failed": 0}
        assert message_sender.send_photo.call_count == 2
        message_sender.send_photo.assert_any_call(mock_bot, 12345, photo, caption)
        message_sender.send_photo.assert_any_call(mock_bot, 67890, photo, caption)

    @pytest.mark.asyncio
    async def test_send_message_to_multiple_video(
        self, message_sender, mock_bot, mock_user_storage, mock_message_logger
    ):
        """Test sending video to multiple users."""
        user_ids = [12345, 67890]
        caption = "Test caption"
        video = "video_file_id"

        # Mock successful sends
        message_sender.send_video = AsyncMock(return_value=True)

        # Call the method
        stats = await message_sender.send_message_to_multiple(
            mock_bot, user_ids, caption, message_type="video", video=video
        )

        # Assertions
        assert stats == {"success": 2, "failed": 0}
        assert message_sender.send_video.call_count == 2
        message_sender.send_video.assert_any_call(mock_bot, 12345, video, caption)
        message_sender.send_video.assert_any_call(mock_bot, 67890, video, caption)

    @pytest.mark.asyncio
    async def test_send_message_to_multiple_document(
        self, message_sender, mock_bot, mock_user_storage, mock_message_logger
    ):
        """Test sending document to multiple users."""
        user_ids = [12345, 67890]
        caption = "Test caption"
        document = "document_file_id"

        # Mock successful sends
        message_sender.send_document = AsyncMock(return_value=True)

        # Call the method
        stats = await message_sender.send_message_to_multiple(
            mock_bot, user_ids, caption, message_type="document", document=document
        )

        # Assertions
        assert stats == {"success": 2, "failed": 0}
        assert message_sender.send_document.call_count == 2
        message_sender.send_document.assert_any_call(mock_bot, 12345, document, caption)
        message_sender.send_document.assert_any_call(mock_bot, 67890, document, caption)
