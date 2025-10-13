"""
Message logger for tracking all messages exchanged between users and the bot.
"""

import logging
from datetime import datetime
from typing import Optional

from telegram import Message as TelegramMessage, Update

from .database import db
from .models import Message

logger = logging.getLogger(__name__)


class MessageLogger:
    """Handles logging of all messages to the database."""

    def log_incoming_message(self, update: Update) -> Optional[int]:
        """
        Log an incoming message from a user.

        Args:
            update: Telegram Update object containing the message

        Returns:
            Message ID in database, or None if logging failed
        """
        if not update.message and not update.callback_query:
            return None

        message = update.message or (update.callback_query.message if update.callback_query else None)
        if not message:
            return None

        try:
            with db.get_session() as session:
                # Determine message type
                message_type = self._get_message_type(message)

                # Extract text content
                text = None
                caption = None
                file_id = None

                if message.text:
                    text = message.text
                elif message.caption:
                    caption = message.caption

                # Get file_id for media messages
                if message.photo:
                    file_id = message.photo[-1].file_id if message.photo else None
                elif message.document:
                    file_id = message.document.file_id
                elif message.video:
                    file_id = message.video.file_id
                elif message.audio:
                    file_id = message.audio.file_id
                elif message.voice:
                    file_id = message.voice.file_id
                elif message.sticker:
                    file_id = message.sticker.file_id
                elif message.video_note:
                    file_id = message.video_note.file_id
                elif message.animation:
                    file_id = message.animation.file_id

                # Create message record
                msg_record = Message(
                    telegram_id=message.from_user.id,
                    chat_id=message.chat_id,
                    message_id=message.message_id,
                    direction="incoming",
                    message_type=message_type,
                    text=text,
                    caption=caption,
                    file_id=file_id,
                    reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
                    created_at=datetime.utcnow(),
                )

                session.add(msg_record)
                session.flush()

                logger.debug(
                    f"Logged incoming message: user_id={message.from_user.id}, "
                    f"type={message_type}, msg_id={message.message_id}"
                )

                return msg_record.id

        except Exception as e:
            logger.error(f"Failed to log incoming message: {e}", exc_info=True)
            return None

    def log_outgoing_message(
        self,
        telegram_id: int,
        chat_id: int,
        sent_message: TelegramMessage,
        message_type: str = "text",
        reply_to_message_id: Optional[int] = None,
    ) -> Optional[int]:
        """
        Log an outgoing message sent by the bot.

        Args:
            telegram_id: User's Telegram ID
            chat_id: Chat ID where message was sent
            sent_message: The sent Telegram Message object
            message_type: Type of message (text, photo, etc.)
            reply_to_message_id: ID of message being replied to

        Returns:
            Message ID in database, or None if logging failed
        """
        try:
            with db.get_session() as session:
                # Extract content from sent message
                text = sent_message.text if hasattr(sent_message, "text") else None
                caption = sent_message.caption if hasattr(sent_message, "caption") else None

                # Get file_id for media messages
                file_id = None
                if hasattr(sent_message, "photo") and sent_message.photo:
                    file_id = sent_message.photo[-1].file_id
                elif hasattr(sent_message, "document") and sent_message.document:
                    file_id = sent_message.document.file_id
                elif hasattr(sent_message, "video") and sent_message.video:
                    file_id = sent_message.video.file_id
                elif hasattr(sent_message, "audio") and sent_message.audio:
                    file_id = sent_message.audio.file_id
                elif hasattr(sent_message, "voice") and sent_message.voice:
                    file_id = sent_message.voice.file_id
                elif hasattr(sent_message, "sticker") and sent_message.sticker:
                    file_id = sent_message.sticker.file_id
                elif hasattr(sent_message, "video_note") and sent_message.video_note:
                    file_id = sent_message.video_note.file_id
                elif hasattr(sent_message, "animation") and sent_message.animation:
                    file_id = sent_message.animation.file_id

                # Create message record
                msg_record = Message(
                    telegram_id=telegram_id,
                    chat_id=chat_id,
                    message_id=sent_message.message_id,
                    direction="outgoing",
                    message_type=message_type,
                    text=text,
                    caption=caption,
                    file_id=file_id,
                    reply_to_message_id=reply_to_message_id,
                    created_at=datetime.utcnow(),
                )

                session.add(msg_record)
                session.flush()

                logger.debug(
                    f"Logged outgoing message: user_id={telegram_id}, "
                    f"type={message_type}, msg_id={sent_message.message_id}"
                )

                return msg_record.id

        except Exception as e:
            logger.error(f"Failed to log outgoing message: {e}", exc_info=True)
            return None

    def _get_message_type(self, message: TelegramMessage) -> str:
        """
        Determine the type of a Telegram message.

        Args:
            message: Telegram Message object

        Returns:
            String representing message type
        """
        if message.text:
            return "text"
        elif message.photo:
            return "photo"
        elif message.document:
            return "document"
        elif message.video:
            return "video"
        elif message.audio:
            return "audio"
        elif message.voice:
            return "voice"
        elif message.sticker:
            return "sticker"
        elif message.contact:
            return "contact"
        elif message.location:
            return "location"
        elif message.poll:
            return "poll"
        elif message.video_note:
            return "video_note"
        elif message.animation:
            return "animation"
        else:
            return "other"

    def get_user_messages(
        self,
        telegram_id: int,
        limit: int = 100,
        direction: Optional[str] = None,
    ) -> list[Message]:
        """
        Retrieve messages for a specific user.

        Args:
            telegram_id: User's Telegram ID
            limit: Maximum number of messages to retrieve
            direction: Filter by direction ('incoming' or 'outgoing'), or None for all

        Returns:
            List of Message objects
        """
        try:
            with db.get_session() as session:
                query = session.query(Message).filter(Message.telegram_id == telegram_id)

                if direction:
                    query = query.filter(Message.direction == direction)

                messages = query.order_by(Message.created_at.desc()).limit(limit).all()

                # Detach from session to avoid issues
                session.expunge_all()

                return messages

        except Exception as e:
            logger.error(f"Failed to retrieve user messages: {e}", exc_info=True)
            return []


# Global message logger instance
message_logger = MessageLogger()