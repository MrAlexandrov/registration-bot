"""
Конфигурация бота - использует новую систему опроса.
"""

from os import getenv

from dotenv import load_dotenv

from .registration_config import registration_survey

load_dotenv()


class Config:
    def __init__(self):
        # Валидация BOT_TOKEN
        self.bot_token = getenv("BOT_TOKEN")
        if not self.bot_token:
            raise ValueError(
                "BOT_TOKEN не найден в переменных окружения! "
                "Убедитесь, что файл .env правильно настроен и содержит BOT_TOKEN=<ваш_токен>"
            )

        # Валидация ROOT_ID
        root_id_str = getenv("ROOT_ID")
        if not root_id_str:
            raise ValueError(
                "ROOT_ID не найден в переменных окружения! "
                "Убедитесь, что файл .env содержит ROOT_ID=<ваш_telegram_id>"
            )

        try:
            self.root_id = int(root_id_str)
        except ValueError as e:
            raise ValueError(f"ROOT_ID должен быть числом, получено: {root_id_str}") from e

        # Поддержка множественных администраторов
        admin_ids_str = getenv("ADMIN_IDS", str(self.root_id))
        try:
            self.admin_ids = {int(id_str.strip()) for id_str in admin_ids_str.split(",") if id_str.strip()}
        except ValueError as e:
            raise ValueError(f"ADMIN_IDS должны быть числами, разделёнными запятыми. Получено: {admin_ids_str}") from e

        if not self.admin_ids:
            raise ValueError("Список администраторов пуст! Проверьте ADMIN_IDS или ROOT_ID")

        # Поддержка множественных получателей таблиц
        table_getters_str = getenv("TABLE_GETTERS", admin_ids_str)
        try:
            self.table_getters = {int(id_str.strip()) for id_str in table_getters_str.split(",") if id_str.strip()}
        except ValueError as e:
            raise ValueError(
                f"TABLE_GETTERS должны быть числами, разделёнными запятыми. Получено: {table_getters_str}"
            ) from e

        if not self.table_getters:
            raise ValueError("Список получателей таблиц пуст! Проверьте TABLE_GETTERS")

        # Используем новую систему конфигурации опроса
        self.survey_config = registration_survey

    # Методы для доступа к конфигурации опроса
    def get_field_by_name(self, field_name: str):
        """Получает конфигурацию поля по имени."""
        return self.survey_config.get_field_by_name(field_name)

    def get_field_by_label(self, label: str):
        """Получает конфигурацию поля по метке."""
        return self.survey_config.get_field_by_label(label)

    def get_editable_fields(self):
        """Возвращает список редактируемых полей."""
        return self.survey_config.get_editable_fields()


config = Config()
