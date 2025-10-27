"""
Модуль для отправки уведомлений о достижении вех регистрации.
Отправляет уведомления в чат staff при достижении 25, 50, 75, 100 и т.д. участников.
"""

import logging

from telegram import Bot

from src.messages import OPTION_WILL_DRIVE_YES

from .database import db
from .message_sender import message_sender
from .models import get_user_model
from .permissions import permission_manager

logger = logging.getLogger(__name__)


class MilestoneNotifier:
    """
    Класс для отслеживания и уведомления о достижении вех регистрации.

    Участниками считаются пользователи, которые:
    1. Ответили "Обязательно! 🤩" на вопрос will_drive
    2. Не являются организаторами (is_staff = 0)
    """

    # Кастомные вехи для уведомлений
    # Можно указать любые значения в любом порядке
    MILESTONES = [130, 140, 150, 160, 170, 180]

    def __init__(self):
        """Инициализация уведомителя вех."""
        self.User = get_user_model()
        self._sent_milestones = set()  # Хранит уже отправленные вехи

    def _get_participant_count(self) -> int:
        """
        Получает количество участников.

        Участники - это пользователи, которые:
        - Ответили "Обязательно! 🤩" на вопрос will_drive
        - Не являются организаторами (is_staff = 0)

        Returns:
            int: Количество участников
        """
        try:
            with db.get_session() as session:
                count = (
                    session.query(self.User)
                    .filter(self.User.will_drive == OPTION_WILL_DRIVE_YES, self.User.is_staff == 0)
                    .count()
                )
                return count
        except Exception as e:
            logger.error(f"Ошибка при подсчете участников: {e}")
            return 0

    def _calculate_milestone(self, count: int) -> int | None:
        """
        Определяет, достигнута ли какая-либо веха на основе количества участников.

        Args:
            count: Количество участников

        Returns:
            int | None: Номер достигнутой вехи или None если веха не достигнута
        """
        # Находим все вехи, которые уже достигнуты, но еще не отправлены
        reached_milestones = [m for m in self.MILESTONES if m <= count and m not in self._sent_milestones]

        # Возвращаем наибольшую из достигнутых вех
        return max(reached_milestones) if reached_milestones else None

    def _format_milestone_message(self, milestone: int, current_count: int) -> str:
        """
        Форматирует сообщение о достижении вехи.

        Args:
            milestone: Номер вехи (25, 50, 75, 100...)
            current_count: Текущее количество участников

        Returns:
            str: Отформатированное сообщение
        """
        emoji_map = {
            130: "💫",
            140: "🌟",
            150: "🎆",
            160: "🚀",
            170: "🔥",
            180: "⭐",
        }

        # Для вех больше 200 используем циклический паттерн
        emoji = emoji_map.get(milestone, emoji_map.get(milestone % 200, "🎉"))

        message = (
            f"{emoji} <b>Ура, ура, ура!</b> {emoji}\n\n" f"У нас зарегистрировано <b>{current_count}</b> участников!\n"
        )

        return message

    async def check_and_notify(self, bot: Bot) -> bool:
        """
        Проверяет количество участников и отправляет уведомление при достижении вехи.

        Args:
            bot: Экземпляр Telegram Bot

        Returns:
            bool: True если уведомление было отправлено, False в противном случае
        """
        try:
            # Получаем текущее количество участников
            current_count = self._get_participant_count()
            logger.debug(f"Текущее количество участников: {current_count}")

            # Вычисляем текущую веху
            milestone = self._calculate_milestone(current_count)

            if milestone is None:
                logger.debug("Веха еще не достигнута")
                return False

            # Проверяем, не отправляли ли мы уже уведомление для этой вехи
            if milestone in self._sent_milestones:
                logger.debug(f"Уведомление для вехи {milestone} уже было отправлено")
                return False

            # Получаем ID чата staff
            staff_chat_id = permission_manager.get_chat_by_type("staff")

            if not staff_chat_id:
                logger.warning("Чат staff не зарегистрирован, уведомление не отправлено")
                return False

            # Форматируем и отправляем сообщение
            message = self._format_milestone_message(milestone, current_count)
            success = await message_sender.send_message(bot, staff_chat_id, message, parse_mode="HTML")

            if success:
                # Помечаем веху как отправленную
                self._sent_milestones.add(milestone)
                logger.info(f"✅ Отправлено уведомление о достижении вехи {milestone} участников")
                return True
            else:
                logger.error(f"Не удалось отправить уведомление о вехе {milestone}")
                return False

        except Exception as e:
            logger.error(f"Ошибка при проверке и отправке уведомления о вехе: {e}", exc_info=True)
            return False

    def reset_milestones(self) -> None:
        """
        Сбрасывает список отправленных вех.
        Полезно для тестирования или при необходимости повторной отправки уведомлений.
        """
        self._sent_milestones.clear()
        logger.info("Список отправленных вех сброшен")

    def get_sent_milestones(self) -> set[int]:
        """
        Возвращает множество уже отправленных вех.

        Returns:
            set[int]: Множество номеров отправленных вех
        """
        return self._sent_milestones.copy()


# Глобальный экземпляр для использования в проекте
milestone_notifier = MilestoneNotifier()
