"""
Модуль для безопасной отправки сообщений с обработкой блокировок и ретраями.
"""

import asyncio
import logging
from typing import Any

from telegram import Bot
from telegram.error import Forbidden, NetworkError, RetryAfter, TelegramError

from .user_storage import user_storage

logger = logging.getLogger(__name__)


class MessageSender:
    """
    Класс для безопасной отправки сообщений через Telegram Bot API.

    Особенности:
    - Автоматическая обработка блокировок пользователями
    - Retry механизм при сетевых ошибках
    - Обработка rate limiting (RetryAfter)
    - Логирование всех операций
    """

    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        Инициализация отправителя сообщений.

        Args:
            max_retries: Максимальное количество попыток отправки
            retry_delay: Базовая задержка между попытками в секундах
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    async def send_message(
        self,
        bot: Bot,
        chat_id: int,
        text: str,
        **kwargs: Any,
    ) -> bool:
        """
        Безопасная отправка сообщения с обработкой ошибок и ретраями.

        Args:
            bot: Экземпляр Telegram Bot
            chat_id: ID чата/пользователя
            text: Текст сообщения
            **kwargs: Дополнительные параметры для send_message (parse_mode, reply_markup и т.д.)

        Returns:
            bool: True если сообщение отправлено успешно, False в противном случае
        """
        # Проверяем, не заблокирован ли бот пользователем
        user = user_storage.get_user(chat_id)
        if user and user.get("is_blocked"):
            logger.info(f"Пользователь {chat_id} заблокировал бота, пропускаем отправку")
            return False

        for attempt in range(1, self.max_retries + 1):
            try:
                await bot.send_message(chat_id=chat_id, text=text, **kwargs)
                logger.debug(f"Сообщение успешно отправлено пользователю {chat_id}")
                return True

            except Forbidden as e:
                # Пользователь заблокировал бота
                logger.warning(f"Пользователь {chat_id} заблокировал бота: {e}")
                self._mark_user_as_blocked(chat_id)
                return False

            except RetryAfter as e:
                # Rate limiting от Telegram
                retry_after = e.retry_after
                logger.warning(f"Rate limit для {chat_id}, ожидание {retry_after} секунд")
                await asyncio.sleep(retry_after)
                # Не считаем это попыткой, просто ждём и пробуем снова
                continue

            except NetworkError as e:
                # Сетевая ошибка - пробуем ещё раз
                if attempt < self.max_retries:
                    delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(
                        f"Сетевая ошибка при отправке сообщения {chat_id} "
                        f"(попытка {attempt}/{self.max_retries}): {e}. "
                        f"Повтор через {delay} сек."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Не удалось отправить сообщение {chat_id} после {self.max_retries} попыток: {e}")
                    return False

            except TelegramError as e:
                # Другие ошибки Telegram API
                logger.error(f"Ошибка Telegram API при отправке сообщения {chat_id}: {e}")
                return False

            except Exception as e:
                # Неожиданная ошибка
                logger.error(f"Неожиданная ошибка при отправке сообщения {chat_id}: {e}", exc_info=True)
                return False

        return False

    def _mark_user_as_blocked(self, user_id: int) -> None:
        """
        Помечает пользователя как заблокировавшего бота.

        Args:
            user_id: ID пользователя
        """
        try:
            user_storage.update_user(user_id, "is_blocked", 1)
            logger.info(f"Пользователь {user_id} помечен как заблокировавший бота")
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса блокировки для {user_id}: {e}")

    async def send_message_to_multiple(
        self,
        bot: Bot,
        user_ids: list[int],
        text: str,
        delay_between: float = 0.05,
        **kwargs: Any,
    ) -> dict[str, int]:
        """
        Отправка сообщения нескольким пользователям с задержкой между отправками.

        Args:
            bot: Экземпляр Telegram Bot
            user_ids: Список ID пользователей
            text: Текст сообщения
            delay_between: Задержка между отправками в секундах (для избежания rate limit)
            **kwargs: Дополнительные параметры для send_message

        Returns:
            dict: Статистика отправки {"success": количество успешных, "failed": количество неудачных}
        """
        stats = {"success": 0, "failed": 0}

        for user_id in user_ids:
            success = await self.send_message(bot, user_id, text, **kwargs)
            if success:
                stats["success"] += 1
            else:
                stats["failed"] += 1

            # Задержка между отправками для избежания rate limit
            if delay_between > 0:
                await asyncio.sleep(delay_between)

        logger.info(f"Массовая рассылка завершена: успешно={stats['success']}, неудачно={stats['failed']}")
        return stats


# Глобальный экземпляр для использования в проекте
message_sender = MessageSender(max_retries=3, retry_delay=1.0)
