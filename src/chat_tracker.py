"""
Chat member tracking for staff chat, counselor chat, and superuser chat.
Automatically updates is_staff and is_counselor fields based on chat membership.
"""

import logging

from telegram import ChatMember, Update
from telegram.ext import ContextTypes

from .permissions import Permission, permission_manager
from .user_storage import user_storage

logger = logging.getLogger(__name__)


class ChatTracker:
    """Tracks chat members and manages staff/counselor status."""

    def __init__(self) -> None:
        self.permission_manager = permission_manager
        self.user_storage = user_storage

    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle chat member updates (joins, leaves, etc.).
        Automatically updates is_staff and is_counselor fields based on chat membership.
        """
        result = update.chat_member
        if not result:
            return

        chat_id = result.chat.id
        user_id = result.new_chat_member.user.id
        old_status = result.old_chat_member.status
        new_status = result.new_chat_member.status

        logger.info(
            f"Chat member update in chat {chat_id}: " f"user {user_id} status changed from {old_status} to {new_status}"
        )

        # Check if this is the staff chat
        staff_chat_id = self.permission_manager.get_chat_by_type("staff")
        if staff_chat_id and chat_id == staff_chat_id:
            await self._handle_staff_chat_update(user_id, old_status, new_status)

        # Check if this is the counselor chat
        counselor_chat_id = self.permission_manager.get_chat_by_type("counselor")
        if counselor_chat_id and chat_id == counselor_chat_id:
            await self._handle_counselor_chat_update(user_id, old_status, new_status)

    async def _handle_staff_chat_update(self, user_id: int, old_status: str, new_status: str) -> None:
        """
        Handle staff chat member updates.
        Grant STAFF permission and set is_staff=1 when user joins, revoke when they leave.
        """
        # User joined or became active in staff chat
        if new_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            if old_status in [ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED]:
                # User joined the chat
                self.permission_manager.grant_permission(
                    user_id,
                    Permission.STAFF,
                    0,  # Granted automatically by system
                )
                # Update is_staff field in database
                self._update_user_staff_status(user_id, is_staff=1)
                logger.info(f"Granted STAFF permission to user {user_id} (joined staff chat)")

        # User left or was removed from staff chat
        elif new_status in [ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED]:
            if old_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                # User left the chat
                self.permission_manager.revoke_permission(user_id, Permission.STAFF)
                # Update is_staff field in database
                self._update_user_staff_status(user_id, is_staff=0)
                logger.info(f"Revoked STAFF permission from user {user_id} (left staff chat)")

    async def _handle_counselor_chat_update(self, user_id: int, old_status: str, new_status: str) -> None:
        """
        Handle counselor chat member updates.
        Set is_counselor=1 when user joins, set is_counselor=0 when they leave.
        """
        # User joined or became active in counselor chat
        if new_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
            if old_status in [ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED]:
                # User joined the chat
                self._update_user_counselor_status(user_id, is_counselor=1)
                logger.info(f"Set is_counselor=1 for user {user_id} (joined counselor chat)")

        # User left or was removed from counselor chat
        elif new_status in [ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED]:
            if old_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                # User left the chat
                self._update_user_counselor_status(user_id, is_counselor=0)
                logger.info(f"Set is_counselor=0 for user {user_id} (left counselor chat)")

    def _update_user_staff_status(self, user_id: int, is_staff: int) -> None:
        """Update is_staff field for a user."""
        try:
            user = self.user_storage.get_user(user_id)
            if user:
                self.user_storage.update_user(user_id, "is_staff", is_staff)
                logger.debug(f"Updated is_staff={is_staff} for user {user_id}")
            else:
                logger.warning(f"User {user_id} not found in database, cannot update is_staff")
        except Exception as e:
            logger.error(f"Error updating is_staff for user {user_id}: {e}")

    def _update_user_counselor_status(self, user_id: int, is_counselor: int) -> None:
        """Update is_counselor field for a user."""
        try:
            user = self.user_storage.get_user(user_id)
            if user:
                self.user_storage.update_user(user_id, "is_counselor", is_counselor)
                logger.debug(f"Updated is_counselor={is_counselor} for user {user_id}")
            else:
                logger.warning(f"User {user_id} not found in database, cannot update is_counselor")
        except Exception as e:
            logger.error(f"Error updating is_counselor for user {user_id}: {e}")

    async def sync_staff_chat_members(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Sync all members of staff chat with STAFF permission and is_staff field.
        This should be called periodically or on bot startup.
        """
        staff_chat_id = self.permission_manager.get_chat_by_type("staff")
        if not staff_chat_id:
            logger.info("No staff chat registered, skipping staff sync")
            return

        try:
            # Get all chat members
            chat = await context.bot.get_chat(staff_chat_id)
            member_count = await chat.get_member_count()

            logger.info(f"Syncing staff chat {staff_chat_id} with {member_count} members")

            # Note: Getting all members requires admin rights and may not work in all chats
            # This is a simplified version - in production you might need a different approach

        except Exception as e:
            logger.error(f"Error syncing staff chat members: {e}")

    async def sync_counselor_chat_members(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Sync all members of counselor chat with is_counselor field.
        This should be called periodically or on bot startup.
        """
        counselor_chat_id = self.permission_manager.get_chat_by_type("counselor")
        if not counselor_chat_id:
            logger.info("No counselor chat registered, skipping counselor sync")
            return

        try:
            # Get all chat members
            chat = await context.bot.get_chat(counselor_chat_id)
            member_count = await chat.get_member_count()

            logger.info(f"Syncing counselor chat {counselor_chat_id} with {member_count} members")

            # Note: Getting all members requires admin rights and may not work in all chats
            # This is a simplified version - in production you might need a different approach

        except Exception as e:
            logger.error(f"Error syncing counselor chat members: {e}")


# Global chat tracker instance
chat_tracker = ChatTracker()
