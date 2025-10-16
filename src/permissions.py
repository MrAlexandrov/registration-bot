"""
Permission management system for the bot.
Handles role-based access control and permission checks.
"""

import logging
from datetime import UTC, datetime
from enum import Enum

from sqlalchemy import BigInteger, Boolean, Column, DateTime, Index, Integer, String
from sqlalchemy.orm import declarative_base

from .config import config
from .database import db

logger = logging.getLogger(__name__)

# Create base for permission models
PermissionBase = declarative_base()


class Permission(str, Enum):
    """Available permissions in the system."""

    ADMIN = "admin"  # Can manage users and permissions
    TABLE_VIEWER = "table_viewer"  # Can get registration tables
    MESSAGE_SENDER = "message_sender"  # Can send messages to users
    STAFF = "staff"  # Staff member (from staff chat)
    # Add more permissions as needed


class UserPermission(PermissionBase):
    """Model for storing user permissions."""

    __tablename__ = "user_permissions"
    __table_args__ = (Index("idx_user_permission", "telegram_id", "permission"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, index=True)
    permission = Column(String(50), nullable=False)
    granted_by = Column(BigInteger, nullable=True)  # Who granted this permission
    created_at = Column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<UserPermission(telegram_id={self.telegram_id}, permission='{self.permission}')>"


class BotChat(PermissionBase):
    """Model for tracking bot chats (staff chat, superuser chat, etc.)."""

    __tablename__ = "bot_chats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, nullable=False, index=True)
    chat_type = Column(String(50), nullable=False)  # 'staff', 'superuser', etc.
    chat_title = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, nullable=False)

    def __repr__(self) -> str:
        return f"<BotChat(chat_id={self.chat_id}, type='{self.chat_type}')>"


class PermissionManager:
    """Manages user permissions and role-based access control."""

    def __init__(self) -> None:
        """Initialize permission manager and create tables."""
        self._create_tables()

    def _create_tables(self) -> None:
        """Create permission tables in the database."""
        try:
            PermissionBase.metadata.create_all(bind=db.engine)
            logger.info("Permission tables created successfully")
        except Exception as e:
            logger.error(f"Error creating permission tables: {e}")
            raise

    def is_root(self, user_id: int) -> bool:
        """
        Check if user is the root superuser.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user is root
        """
        return user_id == config.root_id

    def has_permission(self, user_id: int, permission: Permission) -> bool:
        """
        Check if user has a specific permission.
        Root user always has all permissions.

        Args:
            user_id: Telegram user ID
            permission: Permission to check

        Returns:
            True if user has the permission
        """
        # Root has all permissions
        if self.is_root(user_id):
            return True

        # Check database for permission
        with db.get_session() as session:
            perm = session.query(UserPermission).filter_by(telegram_id=user_id, permission=permission.value).first()
            return perm is not None

    def grant_permission(self, user_id: int, permission: Permission, granted_by: int) -> bool:
        """
        Grant a permission to a user.

        Args:
            user_id: Telegram user ID to grant permission to
            permission: Permission to grant
            granted_by: Telegram user ID who is granting the permission

        Returns:
            True if permission was granted, False if already exists
        """

        with db.get_session() as session:
            # Check if permission already exists
            existing = session.query(UserPermission).filter_by(telegram_id=user_id, permission=permission.value).first()

            if existing:
                logger.info(f"User {user_id} already has permission {permission.value}")
                return False

            # Create new permission
            new_perm = UserPermission(
                telegram_id=user_id, permission=permission.value, granted_by=granted_by, created_at=datetime.now(UTC)
            )
            session.add(new_perm)
            session.commit()
            logger.info(f"Granted {permission.value} to user {user_id} by {granted_by}")
            return True

    def revoke_permission(self, user_id: int, permission: Permission) -> bool:
        """
        Revoke a permission from a user.

        Args:
            user_id: Telegram user ID
            permission: Permission to revoke

        Returns:
            True if permission was revoked, False if not found
        """
        with db.get_session() as session:
            perm = session.query(UserPermission).filter_by(telegram_id=user_id, permission=permission.value).first()

            if not perm:
                logger.info(f"User {user_id} doesn't have permission {permission.value}")
                return False

            session.delete(perm)
            session.commit()
            logger.info(f"Revoked {permission.value} from user {user_id}")
            return True

    def get_user_permissions(self, user_id: int) -> set[str]:
        """
        Get all permissions for a user.

        Args:
            user_id: Telegram user ID

        Returns:
            Set of permission names
        """
        # Root has all permissions
        if self.is_root(user_id):
            return {perm.value for perm in Permission}

        with db.get_session() as session:
            perms = session.query(UserPermission).filter_by(telegram_id=user_id).all()
            return {perm.permission for perm in perms}

    def list_users_with_permission(self, permission: Permission) -> list[int]:
        """
        Get list of all users with a specific permission.

        Args:
            permission: Permission to search for

        Returns:
            List of telegram user IDs
        """
        with db.get_session() as session:
            perms = session.query(UserPermission).filter_by(permission=permission.value).all()
            user_ids = [perm.telegram_id for perm in perms]

            # Always include root
            if config.root_id not in user_ids:
                user_ids.insert(0, config.root_id)

            return user_ids

    def register_chat(self, chat_id: int, chat_type: str, chat_title: str | None = None) -> bool:
        """
        Register a bot chat (staff chat, superuser chat, etc.).

        Args:
            chat_id: Telegram chat ID
            chat_type: Type of chat ('staff', 'superuser', etc.)
            chat_title: Optional chat title

        Returns:
            True if chat was registered, False if already exists
        """

        with db.get_session() as session:
            # Check if chat already exists
            existing = session.query(BotChat).filter_by(chat_id=chat_id).first()

            if existing:
                # Update chat type and title if changed
                if existing.chat_type != chat_type or existing.chat_title != chat_title:
                    existing.chat_type = chat_type
                    existing.chat_title = chat_title
                    existing.is_active = True
                    session.commit()
                    logger.info(f"Updated chat {chat_id} to type {chat_type}")
                return False

            # Create new chat
            new_chat = BotChat(
                chat_id=chat_id,
                chat_type=chat_type,
                chat_title=chat_title,
                is_active=True,
                created_at=datetime.now(UTC),
            )
            session.add(new_chat)
            session.commit()
            logger.info(f"Registered chat {chat_id} as {chat_type}")
            return True

    def get_chat_by_type(self, chat_type: str) -> int | None:
        """
        Get chat ID by type.

        Args:
            chat_type: Type of chat to find

        Returns:
            Chat ID or None if not found
        """
        with db.get_session() as session:
            chat = session.query(BotChat).filter_by(chat_type=chat_type, is_active=True).first()
            return chat.chat_id if chat else None

    def is_staff_member(self, user_id: int) -> bool:
        """
        Check if user is a staff member.
        Staff members are either root or have STAFF permission.

        Args:
            user_id: Telegram user ID

        Returns:
            True if user is staff
        """
        return self.is_root(user_id) or self.has_permission(user_id, Permission.STAFF)


# Global permission manager instance
permission_manager = PermissionManager()
