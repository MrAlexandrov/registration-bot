"""
Автосборщики данных для полей опроса.
Следует принципу Single Responsibility - каждый сборщик отвечает за одну задачу.
"""

from typing import Any, Protocol

from telegram import ChatMember


class AutoCollector(Protocol):
    """Протокол для автосборщиков данных."""

    def collect(self, update: Any) -> str | None:
        """Собирает данные из update."""
        ...


class UsernameAutoCollector:
    """Автосборщик username из Telegram."""

    def collect(self, update: Any) -> str | None:
        """Собирает username из Telegram update."""
        if (
            hasattr(update, "message")
            and update.message
            and hasattr(update.message, "from_user")
            and update.message.from_user
        ):
            return update.message.from_user.username
        return None


class FirstNameAutoCollector:
    """Автосборщик имени из Telegram."""

    def collect(self, update: Any) -> str | None:
        """Собирает имя из Telegram update."""
        if (
            hasattr(update, "message")
            and update.message
            and hasattr(update.message, "from_user")
            and update.message.from_user
        ):
            return update.message.from_user.first_name
        return None


class FullNameAutoCollector:
    """Автосборщик полного имени из Telegram."""

    def collect(self, update: Any) -> str | None:
        """Собирает полное имя из Telegram update."""
        if (
            hasattr(update, "message")
            and update.message
            and hasattr(update.message, "from_user")
            and update.message.from_user
        ):
            user = update.message.from_user
            full_name = user.first_name or ""
            if user.last_name:
                full_name += f" {user.last_name}"
            return full_name.strip() if full_name.strip() else None
        return None


# Фабрика автосборщиков
class StaffStatusAutoCollector:
    """Автосборщик статуса организатора (is_staff)."""

    def __init__(self, permission_manager=None, context=None):
        """
        Инициализация автосборщика статуса организатора.

        Args:
            permission_manager: Менеджер прав доступа
            context: Контекст бота для проверки членства в чате
        """
        self.permission_manager = permission_manager
        self.context = context

    async def collect(self, update: Any) -> int:
        """
        Собирает статус организатора из членства в staff чате.

        Args:
            update: Telegram update объект

        Returns:
            1 если пользователь в staff чате, иначе 0
        """
        if not self.permission_manager or not self.context:
            return 0

        user_id = None
        if hasattr(update, "message") and update.message and hasattr(update.message, "from_user"):
            user_id = update.message.from_user.id
        elif hasattr(update, "callback_query") and update.callback_query:
            user_id = update.callback_query.from_user.id

        if not user_id:
            return 0

        # Получаем ID staff чата
        staff_chat_id = self.permission_manager.get_chat_by_type("staff")
        if not staff_chat_id:
            return 0

        try:
            # Проверяем членство в staff чате
            member = await self.context.bot.get_chat_member(staff_chat_id, user_id)
            if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                return 1
        except Exception:
            # Пользователь не в чате или ошибка
            pass

        return 0


class CounselorStatusAutoCollector:
    """Автосборщик статуса вожатого (is_counselor)."""

    def __init__(self, permission_manager=None, context=None):
        """
        Инициализация автосборщика статуса вожатого.

        Args:
            permission_manager: Менеджер прав доступа
            context: Контекст бота для проверки членства в чате
        """
        self.permission_manager = permission_manager
        self.context = context

    async def collect(self, update: Any) -> int:
        """
        Собирает статус вожатого из членства в counselor чате.

        Args:
            update: Telegram update объект

        Returns:
            1 если пользователь в counselor чате, иначе 0
        """
        if not self.permission_manager or not self.context:
            return 0

        user_id = None
        if hasattr(update, "message") and update.message and hasattr(update.message, "from_user"):
            user_id = update.message.from_user.id
        elif hasattr(update, "callback_query") and update.callback_query:
            user_id = update.callback_query.from_user.id

        if not user_id:
            return 0

        # Получаем ID counselor чата
        counselor_chat_id = self.permission_manager.get_chat_by_type("counselor")
        if not counselor_chat_id:
            return 0

        try:
            # Проверяем членство в counselor чате
            member = await self.context.bot.get_chat_member(counselor_chat_id, user_id)
            if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]:
                return 1
        except Exception:
            # Пользователь не в чате или ошибка
            pass

        return 0


# Фабрика автосборщиков
class AutoCollectorFactory:
    """Фабрика для создания автосборщиков."""

    @staticmethod
    def create_username() -> UsernameAutoCollector:
        return UsernameAutoCollector()

    @staticmethod
    def create_first_name() -> FirstNameAutoCollector:
        return FirstNameAutoCollector()

    @staticmethod
    def create_full_name() -> FullNameAutoCollector:
        return FullNameAutoCollector()

    @staticmethod
    def create_staff_status(permission_manager=None, context=None) -> StaffStatusAutoCollector:
        return StaffStatusAutoCollector(permission_manager, context)

    @staticmethod
    def create_counselor_status(permission_manager=None, context=None) -> CounselorStatusAutoCollector:
        return CounselorStatusAutoCollector(permission_manager, context)


# Функции-обертки для обратной совместимости
def auto_collect_username(update: Any) -> str | None:
    return AutoCollectorFactory.create_username().collect(update)


def auto_collect_first_name(update: Any) -> str | None:
    return AutoCollectorFactory.create_first_name().collect(update)


def auto_collect_full_name(update: Any) -> str | None:
    return AutoCollectorFactory.create_full_name().collect(update)


async def auto_collect_staff_status(update: Any, permission_manager=None, context=None) -> int:
    """Асинхронная функция для сбора статуса организатора."""
    collector = AutoCollectorFactory.create_staff_status(permission_manager, context)
    return await collector.collect(update)


async def auto_collect_counselor_status(update: Any, permission_manager=None, context=None) -> int:
    """Асинхронная функция для сбора статуса вожатого."""
    collector = AutoCollectorFactory.create_counselor_status(permission_manager, context)
    return await collector.collect(update)
