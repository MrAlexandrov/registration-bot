"""
Конфигурация бота - использует новую систему опроса.
"""
from os import getenv
from dotenv import load_dotenv
from typing import Set
from .registration_config import registration_survey

load_dotenv()


class Config:
    def __init__(self):
        self.bot_token = getenv('BOT_TOKEN')
        if not self.bot_token:
            raise ValueError("Токен не найден! Убедитесь, что файл .env правильно настроен.")

        # Парсим ID администраторов из переменных окружения
        self.root_id = int(getenv('ROOT_ID'))

        # Поддержка множественных администраторов
        admin_ids_str = getenv('ADMIN_IDS', str(self.root_id))
        self.admin_ids = {int(id_str.strip()) for id_str in admin_ids_str.split(',') if id_str.strip()}

        # Поддержка LENA_ID для обратной совместимости
        lena_id = getenv('LENA_ID')
        if lena_id:
            lena_id = int(lena_id)
            # Поддержка множественных получателей таблиц
            table_getters_str = getenv('TABLE_GETTERS', f"{admin_ids_str},{lena_id}")
            self.table_getters = {int(id_str.strip()) for id_str in table_getters_str.split(',') if id_str.strip()}
        else:
            table_getters_str = getenv('TABLE_GETTERS', admin_ids_str)
            self.table_getters = {int(id_str.strip()) for id_str in table_getters_str.split(',') if id_str.strip()}

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
