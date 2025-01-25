from telegram import (
    # Update, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
)
# import telegram
# from telegram.ext import CallbackContext
from user_storage import user_storage
from settings import FIELDS, POST_REGISTRATION_STATES, ADMIN_STATES, LABELS, ADMIN_IDS, TABLE_GETTERS
from telegram.constants import ParseMode
from utils import get_actual_table
from constants import *


class RegistrationFlow:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.steps = [field[STATE] for field in FIELDS]
        self.states_config = {state[STATE]: state for state in POST_REGISTRATION_STATES}
        self.admin_states_config = {state[STATE]: state for state in ADMIN_STATES}

    async def handle_command(self, update, context):
        """Обрабатывает команды, такие как /start."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)

        if not user:
            print(f"[DEBUG] Создание нового пользователя {user_id}")
            self.user_storage.create_user(user_id)
            await self.transition_state(update, context, self.steps[0])
        else:
            print(f"[DEBUG] Пользователь {user_id} уже существует в состоянии '{user[STATE]}'")
            await self.transition_state(update, context, user[STATE])

    async def try_auto_collect_nickname(self, update, context, state, user_id):
        username = update.message.from_user.username
        if username:  # Ник есть в Telegram
            self.user_storage.update_user(user_id, USERNAME, username)
            await context.bot.send_message(chat_id=user_id, text=f"Твой ник @{username} сохранен автоматически.")
            next_state = self.get_next_state(state)
            await self.transition_state(update, context, next_state)
            return True
        return False

    async def try_skip_education_questions(self, update, context, state, user_id, user_data):
        if state == OTHER_EDUCATION:
            if user_data[EDUCATION_CHOICE] != OTHER_STUDY_PLACE:
                self.user_storage.update_user(user_id, OTHER_EDUCATION, NO)
                # await context.bot.send_message(chat_id=user_id, text="Другое учебное заведение заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return True

        if state == STUDY_GROUP:
            if user_data[EDUCATION_CHOICE] == FINISHED or user_data[EDUCATION_CHOICE] == DO_NOT_STUDY:
                self.user_storage.update_user(user_id, STUDY_GROUP, NO)
                # await context.bot.send_message(chat_id=user_id, text="Учебную группу заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return True

        if state == RESCHEDULING_SESSION:
            if user_data[EDUCATION_CHOICE] == FINISHED or user_data[EDUCATION_CHOICE] == DO_NOT_STUDY:
                self.user_storage.update_user(user_id, RESCHEDULING_SESSION, NO)
                # await context.bot.send_message(chat_id=user_id, text="Информацию про перенос сессии заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return True

        if state == RESCHEDULING_PRACTICE:
            if user_data[EDUCATION_CHOICE] == FINISHED or user_data[EDUCATION_CHOICE] == DO_NOT_STUDY:
                self.user_storage.update_user(user_id, RESCHEDULING_PRACTICE, NO)
                # await context.bot.send_message(chat_id=user_id, text="Информацию про перенос практики заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return True

        return False

    async def transition_state(self, update, context, state):
        user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
        user_data = self.user_storage.get_user(user_id)
        print(f"[DEBUG] Переход к состоянию '{state}' для пользователя {user_id}")

        # Находим конфигурацию состояния
        config = self.get_config_by_state(state)
        if not config:
            if user_id in ADMIN_IDS or user_id:
                config = self.get_admin_config_by_state(state)
            else:
                print(f"[ERROR] Конфигурация для состояния '{state}' не найдена.")
                await context.bot.send_message(
                    chat_id=user_id, 
                    text="Что-то пошло не так 😢\nПопробуй перезапустить меня командой `/start` (все введённые данные я помню), если это не поможет, обратись, пожалуйста, к людям, отвечающим за регистрацию",
                    parse_mode=ParseMode.MARKDOWN,
                )
                return

        # Если это состояние для сбора никнейма, обработать его сразу
        if state == USERNAME:
            if await self.try_auto_collect_nickname(update, context, state, user_id):
                return

        if state in {OTHER_EDUCATION, STUDY_GROUP, RESCHEDULING_SESSION, RESCHEDULING_PRACTICE}:
            if await self.try_skip_education_questions(update, context, state, user_id, user_data):
                return

        if state == WORK_PLACE:
            if user_data[WORK] == NO:
                self.user_storage.update_user(user_id, WORK_PLACE, user_data[WORK])
                # await context.bot.send_message(chat_id=user_id, text="Место работы заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        # Сохраняем текущее состояние
        self.user_storage.update_state(user_id, state)

        # Генерируем сообщение состояния
        message = self.get_state_message(config, user_id)

        actual_field_name = state.replace("edit_", "")
        if OPTIONS in config:
            selected_options = user_data.get(actual_field_name, "")
            selected_options = selected_options.split(", ") if selected_options else []
            reply_markup = self.create_inline_keyboard(
                config[OPTIONS],
                selected_options=selected_options,
                multi_select=config.get(MULTI_SELECT, False)
            )
        elif BUTTONS in config:
            buttons = config[BUTTONS]() if callable(config[BUTTONS]) else config[BUTTONS]

            if state == EDIT:
                user_nickname = user_data.get(USERNAME, "")

                # Убираем кнопку "Изменить ник", если ник уже установлен
                if user_nickname:
                    buttons = [button for button in buttons if button != LABELS[USERNAME]]

            if user_id in ADMIN_IDS or user_id in TABLE_GETTERS and state == REGISTERED:
                if user_id in ADMIN_IDS and SEND_MESSAGE_ALL_USERS not in buttons:
                    buttons.append(SEND_MESSAGE_ALL_USERS)
                if user_id in TABLE_GETTERS and GET_ACTUAL_TABLE not in buttons:
                    buttons.append(GET_ACTUAL_TABLE)

            reply_markup = ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True, one_time_keyboard=True)
        elif config.get(REQUEST_CONTACT):
            reply_markup = ReplyKeyboardMarkup(
                [[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        else:
            reply_markup = ReplyKeyboardRemove()

        print(f"[DEBUG] Отправка сообщения пользователю {user_id}: {message}")
        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    async def handle_input(self, update, context):
        """Обрабатывает пользовательский ввод для всех состояний."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)
        # For user, that does not saved in db, if send some message
        if user is None:
            await context.bot.send_message(chat_id=user_id, text="Извини, кажется, что-то пошло не так, и я не помню твоих данных, заполни, пожалуйста, их заново")
            await self.handle_command(update, context)
            return
        state = user[STATE]

        print(f"[DEBUG] Пользователь {user_id} находится в состоянии '{state}'")

        if user_id in ADMIN_IDS:
            self.user_storage.update_state(user_id, state)
            config = self.get_admin_config_by_state(state)

            if state == ADMIN_SEND_MESSAGE:
                user_input = update.message.text
                if user_input == CANCEL:
                    await self.transition_state(update, context, REGISTERED)
                    return
                all_users_id = self.user_storage.get_all_users()
                print(f"all_users_id = {all_users_id}")
                for current_user_id in all_users_id:
                    try:
                        await context.bot.send_message(chat_id=current_user_id, text=update.message.text)
                    except:
                        print(f"[ERROR] cant sent message for user {current_user_id}")
                await context.bot.send_message(chat_id=user_id, text=f"Сообщение было отправлено {len(all_users_id)} пользователям")
                print(f"[DEBUG] message {update.message.text} was send for {len(all_users_id)} users")
                await self.transition_state(update, context, REGISTERED)
                return

        config = self.get_config_by_state(state)
        if not config:
            print(f"[ERROR] Некорректное состояние '{state}'")
            await context.bot.send_message(
                chat_id=user_id, 
                text="Что-то пошло не так 😢\nПопробуй перезапустить меня командой `/start` (все введённые данные я помню), если это не поможет, обратись, пожалуйста, к людям, отвечающим за регистрацию",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        user_input = update.message.contact.phone_number if update.message.contact else update.message.text

        # Обработка выбора действия (edit, registered)
        if BUTTONS in config:
            await self.process_action_input(update, context, state, user_input)
            return

        # Обработка ввода данных (регистрация/редактирование)
        await self.process_data_input(update, context, state, user_input)

    async def process_action_input(self, update, context, state, user_input):
        """Обрабатывает кнопки в состояниях registered и edit."""
        user_id = update.message.from_user.id

        if state == REGISTERED:
            if user_input == CHANGE_DATA:
                print(f"[DEBUG] Пользователь {user_id} выбрал 'Изменить данные'.")
                await self.transition_state(update, context, EDIT)
                return
            if user_id in ADMIN_IDS or user_id in TABLE_GETTERS:
                if user_id in ADMIN_IDS and user_input == SEND_MESSAGE_ALL_USERS:
                    await self.transition_state(update, context, ADMIN_SEND_MESSAGE)
                    return
                if user_id in TABLE_GETTERS and user_input == GET_ACTUAL_TABLE:
                    file_path = get_actual_table()
                    try:
                        await context.bot.send_document(chat_id=user_id, document=open(file_path, "rb"))
                        await update.message.reply_text("Файл отправлен успешно!")
                    except Exception as e:
                        await update.message.reply_text(f"Не удалось отправить файл: {e}")
                    return

        if state == ADMIN_SEND_MESSAGE:
            if user_input == CANCEL:
                await self.transition_state(update, context)
                return

        if state == EDIT:
            if user_input == CANCEL:
                print(f"[DEBUG] Пользователь {user_id} отменил редактирование.")
                await self.transition_state(update, context, REGISTERED)
                return

            field_config = self.get_config_by_label(user_input)
            if not field_config:
                print(f"[ERROR] Поле '{user_input}' не найдено.")
                await context.bot.send_message(chat_id=user_id, text="Я не знаю такого поля 😢\nВыбери, пожалуйста, другое, или отмени редактирование")
                return

            if field_config[STATE] == USERNAME:
                user_data = self.user_storage.get_user(user_id)
                if user_data[USERNAME]:
                    await context.bot.send_message(chat_id=user_id, text="Я автоматически собрал твой ник в Telegram, если у тебя действительно поменялся аккаунт, напиши людям, отвечающим за регистрацию, они решат вопрос")
                    return

            await self.transition_state(update, context, f"edit_{field_config[STATE]}")

    def apply_db_formatter(self, field_name, value):
        """Применяет форматтер для базы данных, если он указан в конфиге."""
        field_config = next((f for f in FIELDS if f[STATE] == field_name), None)
        db_formatter = field_config.get("db_formatter")
        return db_formatter(value) if db_formatter else value

    async def process_data_input(self, update, context, state, user_input):
        """Обрабатывает пользовательский ввод, проверяет и форматирует перед сохранением."""
        user_id = update.effective_user.id
        user_data = self.user_storage.get_user(user_id)

        # Убираем edit_, чтобы найти конфиг в FIELDS
        actual_state = state.replace("edit_", "")
        field_config = next((f for f in FIELDS if f[STATE] == actual_state), None)

        if not field_config:
            print(f"[ERROR] Поле '{actual_state}' не найдено.")
            await context.bot.send_message(
                chat_id=user_id, 
                text="Что-то пошло не так 😢\nПопробуй перезапустить меня командой `/start` (все введённые данные я помню), если это не поможет, обратись, пожалуйста, к людям, отвечающим за регистрацию",
                parse_mode=ParseMode.MARKDOWN,
            )
            return

        # Если поле требует номер телефона
        if field_config.get(REQUEST_CONTACT) and update.message.contact:
            user_input = update.message.contact.phone_number

        # Проверяем валидатор, если указан
        if field_config.get(VALIDATOR) and not field_config[VALIDATOR](user_input):
            await context.bot.send_message(chat_id=user_id, text=f"Некорректное значение для {field_config['label']}. Попробуй снова.")
            return

        # Форматируем и сохраняем данные
        formatted_db_value = self.apply_db_formatter(actual_state, user_input)
        self.user_storage.update_user(user_id, actual_state, formatted_db_value)

        # Переход к следующему состоянию
        next_state = self.get_next_state(state)
        await self.transition_state(update, context, next_state)

    def get_next_state(self, state):
        actual_state = state.replace("edit_", "")

        if state.startswith("edit_"):
            return REGISTERED  # Возврат к registered после редактирования

        if actual_state in self.steps:
            current_index = self.steps.index(actual_state)
            if current_index < len(self.steps) - 1:
                return self.steps[current_index + 1]

        return REGISTERED

    def get_config_by_state(self, state):
        """Возвращает конфигурацию состояния по имени."""
        print(f"[DEBUG] Поиск конфигурации для состояния '{state}'")

        if state.startswith("edit_"):
            original_field_name = state.replace("edit_", "")
            config = next((f for f in FIELDS if f[STATE] == original_field_name), None)
            if config:
                print(f"[DEBUG] Сгенерирована конфигурация для edit состояния: {config}")
            else:
                print(f"[ERROR] Конфигурация для edit состояния '{state}' не найдена.")
            return config

        config = next((f for f in FIELDS if f[STATE] == state), None) or self.states_config.get(state)
        if config:
            print(f"[DEBUG] Найдена конфигурация для состояния '{state}': {config}")
        else:
            print(f"[ERROR] Конфигурация для состояния '{state}' не найдена.")
        return config

    def get_admin_config_by_state(self, state):
        """Возвращает конфигурацию состояния по имени."""
        print(f"[DEBUG] Поиск конфигурации для состояния '{state}'")

        config = next((f for f in ADMIN_STATES if f[STATE] == state), None) or self.admin_states_config.get(state)

        if config:
            print(f"[DEBUG] Найдена конфигурация для состояния '{state}': {config}")
        else:
            print(f"[ERROR] Конфигурация для состояния '{state}' не найдена.")
        return config

    def get_config_by_label(self, label):
        """Возвращает конфигурацию поля по его label (используется в редактировании)."""
        return next((f for f in FIELDS if f[LABEL] == label), None)

    def get_registered_message(self, config, user_id):
        if config[STATE] != REGISTERED:
            print(f"[ERROR] get_registered_message should use only for register state, current state = {config[STATE]}") 
        user = self.user_storage.get_user(user_id)
        print(f"[DEBUG] Данные пользователя из базы: {user}")

        # Формируем словарь с данными пользователя
        user_data = {
            field[STATE]: field[DISPLAY_FORMATTER](user.get(field[STATE], "Не указано"))
            if DISPLAY_FORMATTER in field and callable(field[DISPLAY_FORMATTER])
            else user.get(field[STATE], "Не указано")
            for field in FIELDS
        }

        print(f"[DEBUG] Подготовленные данные для подстановки: {user_data}")

        # Формируем сообщение с подстановкой данных
        return config[MESSAGE].format(**user_data)

    def get_state_message(self, config, user_id):
        """Формирует сообщение состояния, включая подстановку данных пользователя."""
        print(f"[DEBUG] Формирование сообщения для состояния '{config[STATE]}'")

        if config[STATE] == REGISTERED:
            return self.get_registered_message(config, user_id)

        # Возвращаем стандартное сообщение для других состояний
        return config[MESSAGE]

    async def clear_inline_keyboard(self, update):
        """Удаляет только инлайн-клавиатуру, оставляя текст сообщения."""
        if update.callback_query:
            await update.callback_query.edit_message_reply_markup(reply_markup=None)

    async def handle_inline_query(self, update, context):
        """Обрабатывает нажатия на инлайн-кнопки."""
        query = update.callback_query
        await query.answer()

        # Получаем данные из callback_data
        callback_data = query.data.split('|')
        action = callback_data[0]  # select или done
        option = callback_data[1] if len(callback_data) > 1 else None

        user_id = query.from_user.id
        user = self.user_storage.get_user(user_id)
        state = user[STATE]

        # Преобразование edit_* в основное имя поля
        actual_field_name = state.replace("edit_", "")

        # Проверяем, является ли выбор одиночным или множественным
        field_config = self.get_config_by_state(actual_field_name)
        is_multi_select = field_config.get(MULTI_SELECT, False)

        selected_options = user.get(actual_field_name, "").split(", ") if user.get(actual_field_name) else []

        if action == "select":
            if is_multi_select:
                if option in selected_options:
                    selected_options.remove(option)  # Убираем, если уже выбрано
                else:
                    selected_options.append(option)  # Добавляем, если не выбрано
            else:
                selected_options = [option]  # Для одиночного выбора заменяем на текущий выбор
                # Удаляем только клавиатуру
                await self.clear_inline_keyboard(update)

                # Обновляем выбранные значения в базе
                self.user_storage.update_user(user_id, actual_field_name, ", ".join(selected_options))

                # Определяем следующее состояние
                next_state = self.get_next_state(state)
                print(f"[DEBUG] Переход к следующему состоянию: {next_state}")

                # Переход к следующему состоянию
                await self.transition_state(update, context, next_state)
                return

            # Обновляем выбранные значения в базе
            self.user_storage.update_user(user_id, actual_field_name, ", ".join(selected_options))

            # Формируем кнопки
            buttons = [
                InlineKeyboardButton(
                    f"✅ {opt}" if opt in selected_options else opt,
                    callback_data=f"select|{opt}"
                )
                for opt in field_config[OPTIONS]
            ]

            # Кнопки в две колонки
            buttons = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            buttons.append([InlineKeyboardButton(DONE, callback_data="done")])
            reply_markup = InlineKeyboardMarkup(buttons)

            if query.message.reply_markup != reply_markup:
                await query.edit_message_reply_markup(reply_markup=reply_markup)
            else:
                print("[DEBUG] Reply markup is not modified, skipping edit_message_reply_markup call")

        elif action == "done":
            if not selected_options:
                await context.bot.send_message(chat_id=user_id, text="Нужно что-то выбрать!")
                return
            # Удаляем только клавиатуру
            await self.clear_inline_keyboard(update)

            # Определяем следующее состояние
            next_state = self.get_next_state(state)
            print(f"[DEBUG] Переход к следующему состоянию: {next_state}")

            # Переход к следующему состоянию
            await self.transition_state(update, context, next_state)

    def create_inline_keyboard(self, options, selected_options=None, multi_select=False):
        selected_options = selected_options or []
        buttons = [
            InlineKeyboardButton(
                f"✅ {opt}" if opt in selected_options else opt,
                callback_data=f"select|{opt}"
            )
            for opt in options
        ]

        # Формируем кнопки в две колонки
        keyboard = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
        if multi_select:
            keyboard.append([InlineKeyboardButton(DONE, callback_data="done")])

        return InlineKeyboardMarkup(keyboard)  # Возвращаем объект InlineKeyboardMarkup


# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
