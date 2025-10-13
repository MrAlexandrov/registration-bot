"""
Chat member tracking for staff chat and superuser chat.
Automatically grants/revokes STAFF permission based on chat membership.
"""

import logging

from telegram import ChatMember, Update
from telegram.ext import ContextTypes

from .permissions import Permission, permission_manager

logger = logging.getLogger(__name__)


class ChatTracker:
    """Tracks chat members and manages staff permissions."""

    def __init__(self) -> None:
        self.permission_manager = permission_manager

    async def handle_chat_member_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handle chat member updates (joins, leaves, etc.).
        Automatically grants/revokes STAFF permission for staff chat members.
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

    async def _handle_staff_chat_update(self, user_id: int, old_status: str, new_status: str) -> None:
        """
        Handle staff chat member updates.
        Grant STAFF permission when user joins, revoke when they leave.
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
                logger.info(f"Granted STAFF permission to user {user_id} (joined staff chat)")

        # User left or was removed from staff chat
        elif new_status in [ChatMember.LEFT, ChatMember.KICKED, ChatMember.BANNED]:
            if old_status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                # User left the chat
                self.permission_manager.revoke_permission(user_id, Permission.STAFF)
                logger.info(f"Revoked STAFF permission from user {user_id} (left staff chat)")

    async def sync_staff_chat_members(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Sync all members of staff chat with STAFF permission.
        This should be called periodically or on bot startup.
        """
        staff_chat_id = self.permission_manager.get_chat_by_type("staff")
        if not staff_chat_id:
            logger.info("No staff chat registered, skipping sync")
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


# Global chat tracker instance
chat_tracker = ChatTracker()
