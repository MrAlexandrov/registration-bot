from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from user_storage import user_storage
from settings import FIELDS, ADMIN_IDS, TABLE_GETTERS
from telegram.constants import ParseMode
from message_formatter import MessageFormatter
from utils import get_actual_table
import logging
from constants import *
from state_handler import StateHandler

logger = logging.getLogger(__name__)


class RegistrationFlow:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.state_handler = StateHandler(user_storage)
        self.steps = [field[STATE] for field in FIELDS]

    async def handle_command(self, update, context):
        """Обрабатывает команды, такие как /start."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)

        if not user:
            logger.info(f"Creating new user for user_id: {user_id}")
            self.user_storage.create_user(user_id)
            await self.state_handler.transition_state(update, context, self.steps[0])
        else:
            logger.info(f"User {user_id} already exists in state '{user[STATE]}'")
            await self.state_handler.transition_state(update, context, user[STATE])

    async def handle_input(self, update, context):
        """Обрабатывает пользовательский ввод для всех состояний."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)
        if user is None:
            await context.bot.send_message(chat_id=user_id, text="Извини, кажется, что-то пошло не так, и я не помню твоих данных, заполни, пожалуйста, их заново")
            await self.handle_command(update, context)
            return
        state = user[STATE]
        logger.info(f"User {user_id} is in state '{state}'")

        if user_id in ADMIN_IDS:
            if await self.handle_admin_input(update, context, state):
                return

        config = self.state_handler.get_config_by_state(state)
        if not config:
            logger.error(f"Invalid state '{state}' for user {user_id}")
            await context.bot.send_message(
                chat_id=user_id,
                text="Что-то пошло не так 😢\nПопробуй перезапустить меня командой `/start` (все введённые данные я помню), если это не поможет, обратись, пожалуйста, к людям, отвечающим за регистрацию",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if OPTIONS in config:
            logger.debug("User sent message while inline keyboard is active")
            await context.bot.send_message(
                chat_id=user_id,
                text="Пожалуйста, воспользуйся кнопками"
            )
            return

        user_input = update.message.contact.phone_number if update.message.contact else update.message.text

        if BUTTONS in config:
            await self.process_action_input(update, context, state, user_input)
            return

        await self.process_data_input(update, context, state, user_input)

    async def handle_admin_input(self, update, context, state):
        user_id = update.message.from_user.id
        if state == ADMIN_SEND_MESSAGE:
            user_input = MessageFormatter.get_escaped_text(update.message)
            if user_input == CANCEL:
                await self.state_handler.transition_state(update, context, REGISTERED)
                return True
            all_users_id = self.user_storage.get_all_users()
            logger.info(f"Sending message to all users: {all_users_id}")
            for current_user_id in all_users_id:
                try:
                    await context.bot.send_message(chat_id=current_user_id, text=user_input, parse_mode=ParseMode.MARKDOWN_V2)
                except Exception as e:
                    logger.error(f"Can't send message to user {current_user_id}: {e}")
            await context.bot.send_message(chat_id=user_id, text=f"Сообщение было отправлено {len(all_users_id)} пользователям")
            logger.info(f"Message '{update.message.text}' was sent to {len(all_users_id)} users")
            await self.state_handler.transition_state(update, context, REGISTERED)
            return True
        return False

    async def process_action_input(self, update, context, state, user_input):
        """Обрабатывает кнопки в состояниях registered и edit."""
        user_id = update.message.from_user.id

        if state == REGISTERED:
            if user_input == CHANGE_DATA:
                logger.info(f"User {user_id} chose 'Change data'")
                await self.state_handler.transition_state(update, context, EDIT)
            elif user_id in ADMIN_IDS and user_input == SEND_MESSAGE_ALL_USERS:
                await self.state_handler.transition_state(update, context, ADMIN_SEND_MESSAGE)
            elif user_id in TABLE_GETTERS and user_input == GET_ACTUAL_TABLE:
                file_path = get_actual_table()
                try:
                    await context.bot.send_document(chat_id=user_id, document=open(file_path, "rb"))
                    await update.message.reply_text("Файл отправлен успешно!")
                except Exception as e:
                    logger.error(f"Failed to send file to user {user_id}: {e}")
                    await update.message.reply_text(f"Не удалось отправить файл: {e}")
        elif state == ADMIN_SEND_MESSAGE and user_input == CANCEL:
            await self.state_handler.transition_state(update, context, REGISTERED)
        elif state == EDIT:
            if user_input == CANCEL:
                logger.info(f"User {user_id} canceled editing")
                await self.state_handler.transition_state(update, context, REGISTERED)
                return

            field_config = self.get_config_by_label(user_input)
            if not field_config:
                logger.error(f"Field '{user_input}' not found for user {user_id}")
                await context.bot.send_message(chat_id=user_id, text="Я не знаю такого поля 😢\nВыбери, пожалуйста, другое, или отмени редактирование")
                return

            if field_config[STATE] == USERNAME:
                user_data = self.user_storage.get_user(user_id)
                if user_data.get(USERNAME):
                    await context.bot.send_message(chat_id=user_id, text="Я автоматически собрал твой ник в Telegram, если у тебя действительно поменялся аккаунт, напиши людям, отвечающим за регистрацию, они решат вопрос")
                    return

            await self.state_handler.transition_state(update, context, f"edit_{field_config[STATE]}")

    def apply_db_formatter(self, field_name, value):
        """Применяет форматтер для базы данных, если он указан в конфиге."""
        field_config = next((f for f in FIELDS if f[STATE] == field_name), None)
        if field_config and "db_formatter" in field_config:
            return field_config["db_formatter"](value)
        return value

    async def process_data_input(self, update, context, state, user_input):
        """Обрабатывает пользовательский ввод, проверяет и форматирует перед сохранением."""
        user_id = update.effective_user.id
        actual_state = state.replace("edit_", "")
        field_config = next((f for f in FIELDS if f[STATE] == actual_state), None)

        if not field_config:
            logger.error(f"Field '{actual_state}' not found for user {user_id}")
            await context.bot.send_message(
                chat_id=user_id,
                text="Что-то пошло не так 😢\nПопробуй перезапустить меня командой `/start` (все введённые данные я помню), если это не поможет, обратись, пожалуйста, к людям, отвечающим за регистрацию",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        if field_config.get(REQUEST_CONTACT) and update.message.contact:
            user_input = update.message.contact.phone_number

        if field_config.get(VALIDATOR):
            is_valid, error_message = field_config[VALIDATOR](user_input)
            if not is_valid:
                await context.bot.send_message(chat_id=user_id, text=error_message)
                return

        formatted_db_value = self.apply_db_formatter(actual_state, user_input)
        self.user_storage.update_user(user_id, actual_state, formatted_db_value)

        next_state = self.state_handler.get_next_state(state)
        await self.state_handler.transition_state(update, context, next_state)

    def get_config_by_label(self, label):
        """Возвращает конфигурацию поля по его label (используется в редактировании)."""
        return next((f for f in FIELDS if f.get(LABEL) == label), None)

    async def clear_inline_keyboard(self, update):
        """Удаляет только инлайн-клавиатуру, оставляя текст сообщения."""
        if update.callback_query:
            await update.callback_query.edit_message_reply_markup(reply_markup=None)

    async def handle_inline_query(self, update, context):
        """Обрабатывает нажатия на инлайн-кнопки."""
        query = update.callback_query
        await query.answer()

        callback_data = query.data.split('|')
        action = callback_data[0]
        option = callback_data[1] if len(callback_data) > 1 else None

        user_id = query.from_user.id
        user = self.user_storage.get_user(user_id)
        state = user[STATE]
        actual_field_name = state.replace("edit_", "")
        field_config = self.state_handler.get_config_by_state(actual_field_name)
        is_multi_select = field_config.get(MULTI_SELECT, False)
        selected_options = user.get(actual_field_name, "").split(", ") if user.get(actual_field_name) else []

        if action == "select":
            if is_multi_select:
                if option in selected_options:
                    selected_options.remove(option)
                else:
                    selected_options.append(option)
            else:
                selected_options = [option]

            self.user_storage.update_user(user_id, actual_field_name, ", ".join(selected_options))
            reply_markup = self.state_handler.create_inline_keyboard(
                field_config[OPTIONS],
                selected_options=selected_options
            )
            if query.message.reply_markup != reply_markup:
                await query.edit_message_reply_markup(reply_markup=reply_markup)
            else:
                logger.debug("Reply markup is not modified, skipping edit_message_reply_markup call")

        elif action == "done":
            if not selected_options:
                await context.bot.send_message(chat_id=user_id, text="Нужно что-то выбрать!")
                return
            await self.clear_inline_keyboard(update)
            next_state = self.state_handler.get_next_state(state)
            await self.state_handler.transition_state(update, context, next_state)


# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
