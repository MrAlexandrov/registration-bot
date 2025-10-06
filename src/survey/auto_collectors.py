"""
Автосборщики данных для полей опроса.
Следует принципу Single Responsibility - каждый сборщик отвечает за одну задачу.
"""

from typing import Any, Protocol


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


# Функции-обертки для обратной совместимости
def auto_collect_username(update: Any) -> str | None:
    return AutoCollectorFactory.create_username().collect(update)


def auto_collect_first_name(update: Any) -> str | None:
    return AutoCollectorFactory.create_first_name().collect(update)


def auto_collect_full_name(update: Any) -> str | None:
    return AutoCollectorFactory.create_full_name().collect(update)
