from telegram import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.constants import ParseMode
from settings import FIELDS, POST_REGISTRATION_STATES, ADMIN_STATES, LABELS, ADMIN_IDS, TABLE_GETTERS
from constants import *
import copy
import logging
from utils import get_actual_table
from message_formatter import MessageFormatter

logger = logging.getLogger(__name__)


class StateHandler:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.steps = [field[STATE] for field in FIELDS]
        self.states_config = {state[STATE]: state for state in POST_REGISTRATION_STATES}
        self.admin_states_config = {state[STATE]: state for state in ADMIN_STATES}

    async def transition_state(self, update, context, state):
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
                await context.bot.send_message(
                    chat_id=user_id,
                    text="Что-то пошло не так 😢\nПопробуй перезапустить меня командой `/start` (все введённые данные я помню), если это не поможет, обратись, пожалуйста, к людям, отвечающим за регистрацию",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

        # Generic handling for auto-collect and skip-if
        if AUTO_COLLECT in config:
            value = config[AUTO_COLLECT](update)
            if value:
                self.user_storage.update_user(user_id, state, value)
                await context.bot.send_message(chat_id=user_id, text=f"Твой ник @{value} сохранен автоматически.")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        if SKIP_IF in config and config[SKIP_IF](user_data):
            self.user_storage.update_user(user_id, state, "skipped")
            next_state = self.get_next_state(state)
            await self.transition_state(update, context, next_state)
            return

        self.user_storage.update_state(user_id, state)
        message = self.get_state_message(config, user_id)
        reply_markup = self.get_reply_markup(config, user_id, state, user_data)

        logger.info(f"Sending message to user {user_id}: {message}")
        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    def get_reply_markup(self, config, user_id, state, user_data):
        actual_field_name = state.replace("edit_", "")
        if OPTIONS in config:
            selected_options = user_data.get(actual_field_name, "")
            selected_options = selected_options.split(", ") if selected_options else []
            return self.create_inline_keyboard(
                config[OPTIONS],
                selected_options=selected_options
            )
        elif BUTTONS in config:
            buttons = config[BUTTONS]() if callable(config[BUTTONS]) else copy.deepcopy(config[BUTTONS])
            if state == REGISTERED:
                if (user_id in ADMIN_IDS or user_id in TABLE_GETTERS):
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
                buttons = [field[LABEL] for field in FIELDS if field.get(EDITABLE, True)] + [CANCEL]
            return ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True, one_time_keyboard=True)
        elif config.get(REQUEST_CONTACT):
            return ReplyKeyboardMarkup(
                [[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
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
            config = next((f for f in FIELDS if f[STATE] == original_field_name), None)
            if config:
                logger.debug(f"Generated configuration for edit state: {config}")
            else:
                logger.error(f"Configuration for edit state '{state}' not found")
            return config
        config = next((f for f in FIELDS if f[STATE] == state), None) or self.states_config.get(state)
        if config:
            logger.debug(f"Found configuration for state '{state}': {config}")
        else:
            logger.error(f"Configuration for state '{state}' not found")
        return config

    def get_admin_config_by_state(self, state):
        logger.debug(f"Searching for admin configuration for state '{state}'")
        config = next((f for f in ADMIN_STATES if f[STATE] == state), None) or self.admin_states_config.get(state)
        if config:
            logger.debug(f"Found admin configuration for state '{state}': {config}")
        else:
            logger.error(f"Admin configuration for state '{state}' not found")
        return config

    def get_state_message(self, config, user_id):
        logger.debug(f"Formatting message for state '{config[STATE]}'")
        if config[STATE] == REGISTERED:
            return self.get_registered_message(config, user_id)
        return config[MESSAGE]

    def get_registered_message(self, config, user_id):
        if config[STATE] != REGISTERED:
            logger.error(f"get_registered_message should only be used for the 'registered' state, current state = {config[STATE]}")
        user = self.user_storage.get_user(user_id)
        logger.debug(f"User data from database: {user}")
        user_data = {
            field[STATE]: field[DISPLAY_FORMATTER](user.get(field[STATE], "Не указано"))
            if DISPLAY_FORMATTER in field and callable(field[DISPLAY_FORMATTER])
            else user.get(field[STATE], "Не указано")
            for field in FIELDS
        }
        logger.debug(f"Prepared data for substitution: {user_data}")
        return config[MESSAGE].format(**user_data)

    def create_inline_keyboard(self, options, selected_options=None):
        selected_options = selected_options or []
        buttons = [
            InlineKeyboardButton(
                f"✅ {opt}" if opt in selected_options else opt,
                callback_data=f"select|{opt}"
            )
            for opt in options
        ]
        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        if selected_options:
            keyboard.append([InlineKeyboardButton(DONE, callback_data="done")])
        return InlineKeyboardMarkup(keyboard)
