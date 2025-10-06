"""
Настройки бота - использует новую систему конфигурации.
Все настройки flow находятся в registration_config.py
"""
from .config import config

# Основные настройки бота
BOT_TOKEN = config.bot_token
ADMIN_IDS = config.admin_ids
TABLE_GETTERS = config.table_getters

# Прямой доступ к новой системе конфигурации опроса
SURVEY_CONFIG = config.survey_config
