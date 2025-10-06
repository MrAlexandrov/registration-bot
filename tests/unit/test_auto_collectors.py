"""
Тесты для автосборщиков данных.
"""
import pytest
from unittest.mock import MagicMock
from src.survey.auto_collectors import (
    UsernameAutoCollector,
    FirstNameAutoCollector,
    FullNameAutoCollector,
    AutoCollectorFactory,
    auto_collect_username,
    auto_collect_first_name,
    auto_collect_full_name
)


class TestUsernameAutoCollector:
    """Тесты для UsernameAutoCollector."""

    def test_collect_username_success(self):
        """Тест успешного сбора username."""
        collector = UsernameAutoCollector()

        # Создаем мок update
        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.username = "test_user"

        result = collector.collect(update)
        assert result == "test_user"

    def test_collect_username_no_message(self):
        """Тест сбора username без сообщения."""
        collector = UsernameAutoCollector()

        update = MagicMock()
        update.message = None

        result = collector.collect(update)
        assert result is None

    def test_collect_username_no_user(self):
        """Тест сбора username без пользователя."""
        collector = UsernameAutoCollector()

        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = None

        result = collector.collect(update)
        assert result is None


class TestFirstNameAutoCollector:
    """Тесты для FirstNameAutoCollector."""

    def test_collect_first_name_success(self):
        """Тест успешного сбора имени."""
        collector = FirstNameAutoCollector()

        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.first_name = "Иван"

        result = collector.collect(update)
        assert result == "Иван"

    def test_collect_first_name_no_message(self):
        """Тест сбора имени без сообщения."""
        collector = FirstNameAutoCollector()

        update = MagicMock()
        update.message = None

        result = collector.collect(update)
        assert result is None


class TestFullNameAutoCollector:
    """Тесты для FullNameAutoCollector."""

    def test_collect_full_name_with_last_name(self):
        """Тест сбора полного имени с фамилией."""
        collector = FullNameAutoCollector()

        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.first_name = "Иван"
        update.message.from_user.last_name = "Иванов"

        result = collector.collect(update)
        assert result == "Иван Иванов"

    def test_collect_full_name_without_last_name(self):
        """Тест сбора полного имени без фамилии."""
        collector = FullNameAutoCollector()

        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.first_name = "Иван"
        update.message.from_user.last_name = None

        result = collector.collect(update)
        assert result == "Иван"

    def test_collect_full_name_empty_first_name(self):
        """Тест сбора полного имени с пустым именем."""
        collector = FullNameAutoCollector()

        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.first_name = ""
        update.message.from_user.last_name = "Иванов"

        result = collector.collect(update)
        assert result == "Иванов"


class TestAutoCollectorFactory:
    """Тесты для AutoCollectorFactory."""

    def test_create_username(self):
        """Тест создания UsernameAutoCollector."""
        collector = AutoCollectorFactory.create_username()
        assert isinstance(collector, UsernameAutoCollector)

    def test_create_first_name(self):
        """Тест создания FirstNameAutoCollector."""
        collector = AutoCollectorFactory.create_first_name()
        assert isinstance(collector, FirstNameAutoCollector)

    def test_create_full_name(self):
        """Тест создания FullNameAutoCollector."""
        collector = AutoCollectorFactory.create_full_name()
        assert isinstance(collector, FullNameAutoCollector)


class TestCompatibilityFunctions:
    """Тесты для функций обратной совместимости."""

    def test_auto_collect_username(self):
        """Тест функции auto_collect_username."""
        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.username = "test_user"

        result = auto_collect_username(update)
        assert result == "test_user"

    def test_auto_collect_first_name(self):
        """Тест функции auto_collect_first_name."""
        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.first_name = "Иван"

        result = auto_collect_first_name(update)
        assert result == "Иван"

    def test_auto_collect_full_name(self):
        """Тест функции auto_collect_full_name."""
        update = MagicMock()
        update.message = MagicMock()
        update.message.from_user = MagicMock()
        update.message.from_user.first_name = "Иван"
        update.message.from_user.last_name = "Иванов"

        result = auto_collect_full_name(update)
        assert result == "Иван Иванов"
