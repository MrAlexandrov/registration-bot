"""
Тесты для модуля milestone_notifier.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.milestone_notifier import MilestoneNotifier


@pytest.fixture
def milestone_notifier():
    """Создает экземпляр MilestoneNotifier для тестов."""
    notifier = MilestoneNotifier()
    notifier.reset_milestones()  # Сбрасываем состояние перед каждым тестом
    return notifier


@pytest.fixture
def mock_bot():
    """Создает мок бота."""
    bot = MagicMock()
    bot.send_message = AsyncMock(return_value=True)
    return bot


class TestMilestoneNotifier:
    """Тесты для класса MilestoneNotifier."""

    def test_calculate_milestone_below_threshold(self, milestone_notifier):
        """Тест: веха не достигнута при количестве участников меньше минимальной вехи."""
        assert milestone_notifier._calculate_milestone(0) is None
        assert milestone_notifier._calculate_milestone(5) is None
        assert milestone_notifier._calculate_milestone(9) is None

    def test_calculate_milestone_at_threshold(self, milestone_notifier):
        """Тест: веха достигнута при количестве участников равном вехе."""
        assert milestone_notifier._calculate_milestone(10) == 10
        assert milestone_notifier._calculate_milestone(25) == 25
        assert milestone_notifier._calculate_milestone(50) == 50
        assert milestone_notifier._calculate_milestone(100) == 100

    def test_calculate_milestone_between_milestones(self, milestone_notifier):
        """Тест: возвращается наибольшая достигнутая веха."""
        # Между 10 и 25 должна вернуться 10
        assert milestone_notifier._calculate_milestone(11) == 10
        assert milestone_notifier._calculate_milestone(24) == 10

        # Между 25 и 50 должна вернуться 25
        assert milestone_notifier._calculate_milestone(26) == 25
        assert milestone_notifier._calculate_milestone(49) == 25

        # Между 50 и 75 должна вернуться 50
        assert milestone_notifier._calculate_milestone(51) == 50
        assert milestone_notifier._calculate_milestone(74) == 50

        # Между 100 и 125 должна вернуться 100
        assert milestone_notifier._calculate_milestone(101) == 100
        assert milestone_notifier._calculate_milestone(124) == 100

    def test_calculate_milestone_already_sent(self, milestone_notifier):
        """Тест: уже отправленные вехи не возвращаются."""
        # Отмечаем вехи 10 и 25 как отправленные
        milestone_notifier._sent_milestones.add(10)
        milestone_notifier._sent_milestones.add(25)

        # При 26 участниках вехи 10 и 25 уже отправлены, должно вернуться None
        assert milestone_notifier._calculate_milestone(26) is None

        # При 50 участниках должна вернуться веха 50
        assert milestone_notifier._calculate_milestone(50) == 50

        # Отмечаем веху 50 как отправленную
        milestone_notifier._sent_milestones.add(50)

        # При 51 участнике все вехи до 50 отправлены, должно вернуться None
        assert milestone_notifier._calculate_milestone(51) is None

        # При 75 участниках должна вернуться веха 75
        assert milestone_notifier._calculate_milestone(75) == 75

    def test_format_milestone_message(self, milestone_notifier):
        """Тест: сообщение о вехе форматируется корректно."""
        message = milestone_notifier._format_milestone_message(25, 27)

        assert "27" in message
        assert "🎉" in message

    def test_format_milestone_message_different_milestones(self, milestone_notifier):
        """Тест: разные вехи используют разные эмодзи."""
        message_25 = milestone_notifier._format_milestone_message(25, 25)
        message_50 = milestone_notifier._format_milestone_message(50, 50)
        message_100 = milestone_notifier._format_milestone_message(100, 100)

        # Проверяем, что сообщения содержат правильные числа
        assert "25" in message_25
        assert "50" in message_50
        assert "100" in message_100

    @pytest.mark.asyncio
    async def test_check_and_notify_no_milestone(self, milestone_notifier, mock_bot):
        """Тест: уведомление не отправляется, если веха не достигнута."""
        with patch.object(milestone_notifier, "_get_participant_count", return_value=5):
            result = await milestone_notifier.check_and_notify(mock_bot)

            assert result is False
            mock_bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_and_notify_no_staff_chat(self, milestone_notifier, mock_bot):
        """Тест: уведомление не отправляется, если чат staff не зарегистрирован."""
        with patch.object(milestone_notifier, "_get_participant_count", return_value=10):
            with patch("src.milestone_notifier.permission_manager.get_chat_by_type", return_value=None):
                result = await milestone_notifier.check_and_notify(mock_bot)

                assert result is False
                mock_bot.send_message.assert_not_called()

    @pytest.mark.asyncio
    async def test_check_and_notify_milestone_reached(self, milestone_notifier, mock_bot):
        """Тест: уведомление отправляется при достижении вехи."""
        staff_chat_id = -1001234567890

        with patch.object(milestone_notifier, "_get_participant_count", return_value=10):
            with patch("src.milestone_notifier.permission_manager.get_chat_by_type", return_value=staff_chat_id):
                with patch("src.milestone_notifier.message_sender.send_message", new_callable=AsyncMock) as mock_send:
                    mock_send.return_value = True

                    result = await milestone_notifier.check_and_notify(mock_bot)

                    assert result is True
                    mock_send.assert_called_once()

                    # Проверяем, что веха добавлена в список отправленных
                    assert 10 in milestone_notifier.get_sent_milestones()

    @pytest.mark.asyncio
    async def test_check_and_notify_milestone_already_sent(self, milestone_notifier, mock_bot):
        """Тест: уведомление не отправляется повторно для той же вехи."""
        staff_chat_id = -1001234567890

        with patch.object(milestone_notifier, "_get_participant_count", return_value=10):
            with patch("src.milestone_notifier.permission_manager.get_chat_by_type", return_value=staff_chat_id):
                with patch("src.milestone_notifier.message_sender.send_message", new_callable=AsyncMock) as mock_send:
                    mock_send.return_value = True

                    # Первая отправка
                    result1 = await milestone_notifier.check_and_notify(mock_bot)
                    assert result1 is True

                    # Вторая попытка отправки для той же вехи
                    result2 = await milestone_notifier.check_and_notify(mock_bot)
                    assert result2 is False

                    # Проверяем, что send_message был вызван только один раз
                    assert mock_send.call_count == 1

    @pytest.mark.asyncio
    async def test_check_and_notify_multiple_milestones(self, milestone_notifier, mock_bot):
        """Тест: уведомления отправляются для разных вех."""
        staff_chat_id = -1001234567890

        with patch("src.milestone_notifier.permission_manager.get_chat_by_type", return_value=staff_chat_id):
            with patch("src.milestone_notifier.message_sender.send_message", new_callable=AsyncMock) as mock_send:
                mock_send.return_value = True

                # Достигнута веха 10
                with patch.object(milestone_notifier, "_get_participant_count", return_value=10):
                    result1 = await milestone_notifier.check_and_notify(mock_bot)
                    assert result1 is True

                # Достигнута веха 25
                with patch.object(milestone_notifier, "_get_participant_count", return_value=25):
                    result2 = await milestone_notifier.check_and_notify(mock_bot)
                    assert result2 is True

                # Проверяем, что оба уведомления были отправлены
                assert mock_send.call_count == 2
                assert 10 in milestone_notifier.get_sent_milestones()
                assert 25 in milestone_notifier.get_sent_milestones()

    def test_reset_milestones(self, milestone_notifier):
        """Тест: сброс списка отправленных вех."""
        # Добавляем вехи
        milestone_notifier._sent_milestones.add(10)
        milestone_notifier._sent_milestones.add(25)
        milestone_notifier._sent_milestones.add(50)

        assert len(milestone_notifier.get_sent_milestones()) == 3

        # Сбрасываем
        milestone_notifier.reset_milestones()

        assert len(milestone_notifier.get_sent_milestones()) == 0

    def test_get_sent_milestones(self, milestone_notifier):
        """Тест: получение списка отправленных вех."""
        milestone_notifier._sent_milestones.add(10)
        milestone_notifier._sent_milestones.add(25)
        milestone_notifier._sent_milestones.add(50)

        sent = milestone_notifier.get_sent_milestones()

        assert 10 in sent
        assert 25 in sent
        assert 50 in sent
        assert len(sent) == 3

        # Проверяем, что возвращается копия, а не оригинал
        sent.add(75)
        assert 75 not in milestone_notifier.get_sent_milestones()
