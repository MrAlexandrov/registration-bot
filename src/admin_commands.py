"""
Admin commands for managing users and permissions.
Only accessible to root and users with ADMIN permission.
"""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from .permissions import Permission, permission_manager
from .user_storage import user_storage

logger = logging.getLogger(__name__)


class AdminCommands:
    """Handles admin commands for user and permission management."""

    def __init__(self):
        self.permission_manager = permission_manager

    async def handle_admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Route admin commands to appropriate handlers.

        Commands:
        /grant_permission <user_id> <permission> - Grant permission to user
        /revoke_permission <user_id> <permission> - Revoke permission from user
        /list_permissions <user_id> - List user's permissions
        /list_users <permission> - List users with specific permission
        /register_staff_chat - Register current chat as staff chat
        /register_superuser_chat - Register current chat as superuser chat
        /my_permissions - Show your own permissions
        """
        user_id = update.effective_user.id

        # Extract command from message (handle both /command and /command@botname)
        command_text = update.message.text.split()[0].lower()
        # Remove bot username if present (e.g., /command@botname -> /command)
        command = command_text.split("@")[0]

        # Check if user has admin permission or is root
        if not (
            self.permission_manager.is_root(user_id)
            or self.permission_manager.has_permission(user_id, Permission.ADMIN)
        ):
            await update.message.reply_text("❌ У вас нет прав для выполнения административных команд.")
            return

        handlers = {
            "/grant_permission": self._grant_permission,
            "/revoke_permission": self._revoke_permission,
            "/list_permissions": self._list_permissions,
            "/list_users": self._list_users,
            "/register_staff_chat": self._register_staff_chat,
            "/register_superuser_chat": self._register_superuser_chat,
            "/my_permissions": self._my_permissions,
        }

        handler = handlers.get(command)
        if handler:
            await handler(update, context)
        else:
            await self._show_help(update, context)

    async def _grant_permission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Grant permission to a user."""
        user_id = update.effective_user.id

        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text(
                    "❌ Использование: /grant_permission <user_id> <permission>\n\n"
                    "Доступные права:\n"
                    "• admin - управление пользователями\n"
                    "• table_viewer - просмотр таблиц\n"
                    "• message_sender - отправка сообщений\n"
                    "• staff - статус организатора"
                )
                return

            target_user_id = int(args[0])
            permission_name = args[1].lower()

            # Validate permission
            try:
                permission = Permission(permission_name)
            except ValueError:
                await update.message.reply_text(
                    f"❌ Неизвестное право: {permission_name}\n\n"
                    "Доступные права: admin, table_viewer, message_sender, staff"
                )
                return

            # Grant permission
            success = self.permission_manager.grant_permission(target_user_id, permission, user_id)

            if success:
                await update.message.reply_text(f"✅ Право '{permission_name}' выдано пользователю {target_user_id}")
            else:
                await update.message.reply_text(f"ℹ️ Пользователь {target_user_id} уже имеет право '{permission_name}'")

        except ValueError:
            await update.message.reply_text("❌ Неверный формат user_id")
        except Exception as e:
            logger.error(f"Error granting permission: {e}")
            await update.message.reply_text(f"❌ Ошибка при выдаче прав: {e}")

    async def _revoke_permission(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Revoke permission from a user."""
        try:
            args = context.args
            if len(args) < 2:
                await update.message.reply_text("❌ Использование: /revoke_permission <user_id> <permission>")
                return

            target_user_id = int(args[0])
            permission_name = args[1].lower()

            # Validate permission
            try:
                permission = Permission(permission_name)
            except ValueError:
                await update.message.reply_text(f"❌ Неизвестное право: {permission_name}")
                return

            # Revoke permission
            success = self.permission_manager.revoke_permission(target_user_id, permission)

            if success:
                await update.message.reply_text(
                    f"✅ Право '{permission_name}' отозвано у пользователя {target_user_id}"
                )
            else:
                await update.message.reply_text(f"ℹ️ Пользователь {target_user_id} не имеет права '{permission_name}'")

        except ValueError:
            await update.message.reply_text("❌ Неверный формат user_id")
        except Exception as e:
            logger.error(f"Error revoking permission: {e}")
            await update.message.reply_text(f"❌ Ошибка при отзыве прав: {e}")

    async def _list_permissions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List permissions for a specific user."""
        try:
            args = context.args
            if len(args) < 1:
                await update.message.reply_text("❌ Использование: /list_permissions <user_id>")
                return

            target_user_id = int(args[0])

            # Check if user exists
            user = user_storage.get_user(target_user_id)
            if not user:
                await update.message.reply_text(f"❌ Пользователь {target_user_id} не найден в базе данных")
                return

            # Get permissions
            permissions = self.permission_manager.get_user_permissions(target_user_id)
            is_root = self.permission_manager.is_root(target_user_id)

            message = f"👤 Права пользователя {target_user_id}:\n\n"

            if is_root:
                message += "🔑 ROOT (суперпользователь) - все права\n"
            elif permissions:
                for perm in sorted(permissions):
                    message += f"• {perm}\n"
            else:
                message += "Нет специальных прав"

            await update.message.reply_text(message)

        except ValueError:
            await update.message.reply_text("❌ Неверный формат user_id")
        except Exception as e:
            logger.error(f"Error listing permissions: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def _list_users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """List all users with a specific permission."""
        try:
            args = context.args
            if len(args) < 1:
                await update.message.reply_text(
                    "❌ Использование: /list_users <permission>\n\n"
                    "Доступные права: admin, table_viewer, message_sender, staff"
                )
                return

            permission_name = args[0].lower()

            # Validate permission
            try:
                permission = Permission(permission_name)
            except ValueError:
                await update.message.reply_text(f"❌ Неизвестное право: {permission_name}")
                return

            # Get users with permission
            user_ids = self.permission_manager.list_users_with_permission(permission)

            if not user_ids:
                await update.message.reply_text(f"ℹ️ Нет пользователей с правом '{permission_name}'")
                return

            message = f"👥 Пользователи с правом '{permission_name}':\n\n"
            for uid in user_ids:
                is_root = self.permission_manager.is_root(uid)
                root_marker = " 🔑 (ROOT)" if is_root else ""
                message += f"• {uid}{root_marker}\n"

            await update.message.reply_text(message)

        except Exception as e:
            logger.error(f"Error listing users: {e}")
            await update.message.reply_text(f"❌ Ошибка: {e}")

    async def _register_staff_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Register current chat as staff chat."""
        user_id = update.effective_user.id

        # Only root can register chats
        if not self.permission_manager.is_root(user_id):
            await update.message.reply_text("❌ Только ROOT может регистрировать чаты")
            return

        chat = update.effective_chat
        if chat.type == "private":
            await update.message.reply_text("❌ Эта команда работает только в групповых чатах")
            return

        self.permission_manager.register_chat(chat.id, "staff", chat.title)

        await update.message.reply_text(
            f"✅ Чат '{chat.title}' зарегистрирован как чат организаторов\n\n"
            "Все участники этого чата автоматически получат статус staff"
        )

    async def _register_superuser_chat(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Register current chat as superuser chat."""
        user_id = update.effective_user.id

        # Only root can register chats
        if not self.permission_manager.is_root(user_id):
            await update.message.reply_text("❌ Только ROOT может регистрировать чаты")
            return

        chat = update.effective_chat
        if chat.type == "private":
            await update.message.reply_text("❌ Эта команда работает только в групповых чатах")
            return

        self.permission_manager.register_chat(chat.id, "superuser", chat.title)

        await update.message.reply_text(
            f"✅ Чат '{chat.title}' зарегистрирован как чат суперпользователей\n\n"
            "В этот чат будут отправляться уведомления об ошибках"
        )

    async def _my_permissions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show current user's permissions."""
        user_id = update.effective_user.id

        permissions = self.permission_manager.get_user_permissions(user_id)
        is_root = self.permission_manager.is_root(user_id)

        message = "👤 Ваши права:\n\n"

        if is_root:
            message += "🔑 ROOT (суперпользователь) - все права\n"
        elif permissions:
            for perm in sorted(permissions):
                message += f"• {perm}\n"
        else:
            message += "У вас нет специальных прав"

        await update.message.reply_text(message)

    async def _show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help for admin commands."""
        help_text = """
🔧 Административные команды:

👥 Управление правами:
/grant_permission <user_id> <permission> - Выдать право
/revoke_permission <user_id> <permission> - Отозвать право
/list_permissions <user_id> - Показать права пользователя
/list_users <permission> - Показать пользователей с правом
/my_permissions - Показать ваши права

💬 Управление чатами (только ROOT):
/register_staff_chat - Зарегистрировать чат организаторов
/register_superuser_chat - Зарегистрировать чат суперпользователей

📋 Доступные права:
• admin - управление пользователями и правами
• table_viewer - просмотр таблиц регистрации
• message_sender - отправка сообщений пользователям
• staff - статус организатора
"""
        await update.message.reply_text(help_text)


# Global admin commands instance
admin_commands = AdminCommands()
