import copy
import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.constants import ParseMode

from src.user_storage import UserStorage

from .constants import (
    AUTO_COLLECT,
    BUTTONS,
    CANCEL,
    DONE,
    EDIT,
    GET_ACTUAL_TABLE,
    MESSAGE,
    OPTIONS,
    REGISTERED,
    REQUEST_CONTACT,
    SEND_MESSAGE_ALL_USERS,
    SKIP_IF,
    STATE,
)
from .message_sender import message_sender
from .settings import ADMIN_IDS, SURVEY_CONFIG, TABLE_GETTERS

logger = logging.getLogger(__name__)


class StateHandler:
    def __init__(self, user_storage: UserStorage):
        self.user_storage = user_storage
        self.steps = [field.field_name for field in SURVEY_CONFIG.fields]
        self.states_config = {state[STATE]: state for state in SURVEY_CONFIG.post_registration_states}
        self.admin_states_config = {state[STATE]: state for state in SURVEY_CONFIG.admin_states}

    async def transition_state(self, update: Update, context, state):
        if update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            user_id = update.message.from_user.id

        user_data = self.user_storage.get_user(user_id)
        logger.info(f"Transitioning user {user_id} to state '{state}'")

        config = self.get_config_by_state(state)
        if not config:
            if user_id in ADMIN_IDS:
                config = self.get_admin_config_by_state(state)
            else:
                logger.error(f"Configuration for state '{state}' not found for user {user_id}")
                await message_sender.send_message(
                    context.bot,
                    user_id,
                    "Что-то пошло не так 😢\nПопробуй перезапустить меня командой `/start` (все введённые данные я помню), если это не поможет, обратись, пожалуйста, к людям, отвечающим за регистрацию",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

        # Generic handling for auto-collect and skip-if
        # Use actual field name (without "edit_" prefix) for database operations
        actual_field_name = state.replace("edit_", "")

        # Для SurveyField используем атрибуты, для словарей - ключи
        auto_collect = config.auto_collect if hasattr(config, "auto_collect") else config.get(AUTO_COLLECT)
        if auto_collect:
            value = auto_collect(update)
            if value:
                self.user_storage.update_user(user_id, actual_field_name, value)
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        # Для SurveyField используем атрибуты, для словарей - ключи
        skip_if = config.skip_if if hasattr(config, "skip_if") else config.get(SKIP_IF)
        if skip_if and skip_if(user_data):
            self.user_storage.update_user(user_id, actual_field_name, "skipped")
            next_state = self.get_next_state(state)
            await self.transition_state(update, context, next_state)
            return

        self.user_storage.update_state(user_id, state)
        message = self.get_state_message(config, user_id)
        reply_markup = self.get_reply_markup(config, user_id, state, user_data)

        logger.info(f"Sending message to user {user_id}: {message}")
        await message_sender.send_message(
            context.bot, user_id, message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
        )

    def get_reply_markup(self, config, user_id, state, user_data):
        actual_field_name = state.replace("edit_", "")
        # Для SurveyField используем атрибуты, для словарей - ключи
        if hasattr(config, "options"):
            options = config.options
        else:
            options = config.get(OPTIONS) if isinstance(config, dict) else None

        if options:
            selected_options = user_data.get(actual_field_name, "")
            selected_options = selected_options.split(", ") if selected_options else []
            return self.create_inline_keyboard(options, selected_options=selected_options)
        # Для словарей используем ключи (SurveyField не имеет buttons)
        elif isinstance(config, dict) and BUTTONS in config:
            buttons_value = config[BUTTONS]
            buttons = buttons_value() if callable(buttons_value) else copy.deepcopy(buttons_value)
            if state == REGISTERED:
                if user_id in ADMIN_IDS or user_id in TABLE_GETTERS:
                    if user_id in ADMIN_IDS and SEND_MESSAGE_ALL_USERS not in buttons:
                        buttons.append(SEND_MESSAGE_ALL_USERS)
                    if user_id in TABLE_GETTERS and GET_ACTUAL_TABLE not in buttons:
                        buttons.append(GET_ACTUAL_TABLE)
                else:
                    if SEND_MESSAGE_ALL_USERS in buttons:
                        buttons.remove(SEND_MESSAGE_ALL_USERS)
                    if GET_ACTUAL_TABLE in buttons:
                        buttons.remove(GET_ACTUAL_TABLE)
            if state == EDIT:
                buttons = [field.label for field in SURVEY_CONFIG.get_editable_fields()] + [CANCEL]
            return ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True, one_time_keyboard=True)
        # Для SurveyField используем атрибуты, для словарей - get
        elif (hasattr(config, "request_contact") and config.request_contact) or (
            isinstance(config, dict) and config.get(REQUEST_CONTACT)
        ):
            return ReplyKeyboardMarkup(
                [[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True,
            )
        else:
            return ReplyKeyboardRemove()

    def get_next_state(self, state):
        actual_state = state.replace("edit_", "")
        if state.startswith("edit_"):
            return REGISTERED
        if actual_state in self.steps:
            current_index = self.steps.index(actual_state)
            if current_index < len(self.steps) - 1:
                return self.steps[current_index + 1]
        return REGISTERED

    def get_config_by_state(self, state):
        logger.debug(f"Searching for configuration for state '{state}'")
        if state.startswith("edit_"):
            original_field_name = state.replace("edit_", "")
            config = SURVEY_CONFIG.get_field_by_name(original_field_name)
            if config:
                logger.debug(f"Generated configuration for edit state: {config}")
            else:
                logger.error(f"Configuration for edit state '{state}' not found")
            return config
        config = SURVEY_CONFIG.get_field_by_name(state) or self.states_config.get(state)
        if config:
            logger.debug(f"Found configuration for state '{state}': {config}")
        else:
            logger.error(f"Configuration for state '{state}' not found")
        return config

    def get_admin_config_by_state(self, state):
        logger.debug(f"Searching for admin configuration for state '{state}'")
        config = self.admin_states_config.get(state)
        if config:
            logger.debug(f"Found admin configuration for state '{state}': {config}")
        else:
            logger.error(f"Admin configuration for state '{state}' not found")
        return config

    def get_state_message(self, config, user_id):
        # Для SurveyField используем field_name, для словарей - STATE
        state_name = config.field_name if hasattr(config, "field_name") else config[STATE]
        logger.debug(f"Formatting message for state '{state_name}'")
        if state_name == REGISTERED:
            return self.get_registered_message(config, user_id)
        # Для SurveyField используем message, для словарей - MESSAGE
        return config.message if hasattr(config, "message") else config[MESSAGE]

    def get_registered_message(self, config, user_id):
        state_name = config.field_name if hasattr(config, "field_name") else config[STATE]
        if state_name != REGISTERED:
            logger.error(
                f"get_registered_message should only be used for the 'registered' state, current state = {state_name}"
            )
        user = self.user_storage.get_user(user_id)
        logger.debug(f"User data from database: {user}")

        # Получаем message из конфига
        message = config.message if hasattr(config, "message") else config[MESSAGE]

        # Проверяем, является ли message функцией (новая система) или строкой (старая система)
        if callable(message):
            # Новая система - вызываем функцию с данными пользователя
            return message(user)
        else:
            # Старая система - форматируем строку
            user_data = {
                field.field_name: (
                    field.display_formatter(user.get(field.field_name, "Не указано"))
                    if field.display_formatter and callable(field.display_formatter)
                    else user.get(field.field_name, "Не указано")
                )
                for field in SURVEY_CONFIG.fields
            }
            logger.debug(f"Prepared data for substitution: {user_data}")
            return message.format(**user_data)

    def create_inline_keyboard(self, options, selected_options=None):
        selected_options = selected_options or []
        buttons = [
            InlineKeyboardButton(f"✅ {opt}" if opt in selected_options else opt, callback_data=f"select|{opt}")
            for opt in options
        ]
        keyboard = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        if selected_options:
            keyboard.append([InlineKeyboardButton(DONE, callback_data="done")])
        return InlineKeyboardMarkup(keyboard)
