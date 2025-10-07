"""
Helper functions for checking permissions in handlers.
Provides convenient decorators and utility functions.
"""

import logging
from functools import wraps

from telegram import Update
from telegram.ext import ContextTypes

from .permissions import Permission, permission_manager

logger = logging.getLogger(__name__)


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission for a handler.

    Usage:
        @require_permission(Permission.ADMIN)
        async def my_handler(update, context):
            # Handler code
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id

            if not permission_manager.has_permission(user_id, permission):
                await update.message.reply_text(
                    f"❌ У вас нет прав для выполнения этой команды.\n" f"Требуется право: {permission.value}"
                )
                logger.warning(
                    f"User {user_id} attempted to use {func.__name__} " f"without {permission.value} permission"
                )
                return

            return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator


def require_root():
    """
    Decorator to require ROOT access for a handler.

    Usage:
        @require_root()
        async def my_handler(update, context):
            # Handler code
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id

            if not permission_manager.is_root(user_id):
                await update.message.reply_text("❌ Эта команда доступна только ROOT пользователю.")
                logger.warning(f"User {user_id} attempted to use {func.__name__} " f"without ROOT access")
                return

            return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator


def require_staff():
    """
    Decorator to require STAFF status for a handler.

    Usage:
        @require_staff()
        async def my_handler(update, context):
            # Handler code
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id

            if not permission_manager.is_staff_member(user_id):
                await update.message.reply_text("❌ Эта команда доступна только организаторам.")
                logger.warning(f"User {user_id} attempted to use {func.__name__} " f"without STAFF status")
                return

            return await func(update, context, *args, **kwargs)

        return wrapper

    return decorator


def can_view_tables(user_id: int) -> bool:
    """
    Check if user can view registration tables.

    Args:
        user_id: Telegram user ID

    Returns:
        True if user has permission
    """
    return permission_manager.has_permission(user_id, Permission.TABLE_VIEWER)


def can_send_messages(user_id: int) -> bool:
    """
    Check if user can send messages to registered users.

    Args:
        user_id: Telegram user ID

    Returns:
        True if user has permission
    """
    return permission_manager.has_permission(user_id, Permission.MESSAGE_SENDER)


def can_manage_users(user_id: int) -> bool:
    """
    Check if user can manage other users and permissions.

    Args:
        user_id: Telegram user ID

    Returns:
        True if user has permission
    """
    return permission_manager.has_permission(user_id, Permission.ADMIN)


def is_staff(user_id: int) -> bool:
    """
    Check if user is a staff member.

    Args:
        user_id: Telegram user ID

    Returns:
        True if user is staff
    """
    return permission_manager.is_staff_member(user_id)
