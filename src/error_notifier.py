"""
Error notification system for superuser chat.
Sends error notifications to the registered superuser chat.
"""

import logging
import traceback
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from .permissions import permission_manager

logger = logging.getLogger(__name__)


class ErrorNotifier:
    """Handles error notifications to superuser chat."""

    def __init__(self) -> None:
        self.permission_manager = permission_manager

    async def notify_error(
        self,
        context: ContextTypes.DEFAULT_TYPE,
        error: Exception,
        update: Update | None = None,
        additional_info: str | None = None,
    ) -> None:
        """
        Send error notification to superuser chat.

        Args:
            context: Bot context
            error: Exception that occurred
            update: Optional update that caused the error
            additional_info: Optional additional information
        """
        superuser_chat_id = self.permission_manager.get_chat_by_type("superuser")

        if not superuser_chat_id:
            logger.warning("No superuser chat registered, cannot send error notification")
            return

        try:
            # Format error message
            message = self._format_error_message(error, update, additional_info)

            # Send to superuser chat
            await context.bot.send_message(chat_id=superuser_chat_id, text=message, parse_mode="HTML")

            logger.info(f"Error notification sent to superuser chat {superuser_chat_id}")

        except Exception as e:
            logger.error(f"Failed to send error notification: {e}")

    def _format_error_message(
        self, error: Exception, update: Update | None = None, additional_info: str | None = None
    ) -> str:
        """
        Format error message for notification.

        Args:
            error: Exception that occurred
            update: Optional update that caused the error
            additional_info: Optional additional information

        Returns:
            Formatted error message
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        message = "🚨 <b>Ошибка в боте</b>\n\n"
        message += f"⏰ Время: {timestamp}\n"
        message += f"❌ Тип: {type(error).__name__}\n"
        message += f"📝 Сообщение: {str(error)}\n"

        if update:
            message += f"\n👤 Пользователь: {update.effective_user.id}"
            if update.effective_user.username:
                message += f" (@{update.effective_user.username})"
            message += "\n"

            if update.message:
                message += f"💬 Сообщение: {update.message.text[:100]}\n"
            elif update.callback_query:
                message += f"🔘 Callback: {update.callback_query.data}\n"

        if additional_info:
            message += f"\nℹ️ Доп. информация:\n{additional_info}\n"

        # Add traceback (truncated if too long)
        tb = traceback.format_exception(type(error), error, error.__traceback__)
        tb_text = "".join(tb)

        if len(tb_text) > 500:
            tb_text = tb_text[:500] + "\n... (обрезано)"

        message += f"\n📋 Traceback:\n<code>{tb_text}</code>"

        # Telegram message limit is 4096 characters
        if len(message) > 4000:
            message = message[:4000] + "\n... (обрезано)"

        return message

    async def notify_info(self, context: ContextTypes.DEFAULT_TYPE, title: str, message: str) -> None:
        """
        Send informational notification to superuser chat.

        Args:
            context: Bot context
            title: Notification title
            message: Notification message
        """
        superuser_chat_id = self.permission_manager.get_chat_by_type("superuser")

        if not superuser_chat_id:
            logger.warning("No superuser chat registered, cannot send notification")
            return

        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            formatted_message = f"ℹ️ <b>{title}</b>\n\n"
            formatted_message += f"⏰ {timestamp}\n\n"
            formatted_message += message

            await context.bot.send_message(chat_id=superuser_chat_id, text=formatted_message, parse_mode="HTML")

            logger.info(f"Info notification sent to superuser chat {superuser_chat_id}")

        except Exception as e:
            logger.error(f"Failed to send info notification: {e}")


# Global error notifier instance
error_notifier = ErrorNotifier()
