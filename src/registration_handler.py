from telegram import (
    Update, 
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    ReplyKeyboardRemove, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
)
import telegram
from telegram.ext import CallbackContext
from user_storage import user_storage
from settings import FIELDS, POST_REGISTRATION_STATES
from telegram.constants import ParseMode


class RegistrationFlow:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.steps = [field["name"] for field in FIELDS]
        self.states_config = {state["name"]: state for state in POST_REGISTRATION_STATES}

    async def handle_command(self, update, context):
        """Обрабатывает команды, такие как /start."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)

        if not user:
            print(f"[DEBUG] Создание нового пользователя {user_id}")
            self.user_storage.create_user(user_id)
            await self.transition_state(update, context, self.steps[0])
        else:
            print(f"[DEBUG] Пользователь {user_id} уже существует в состоянии '{user['state']}'")
            await self.transition_state(update, context, user["state"])

    async def transition_state(self, update, context, state):
        user_id = update.message.from_user.id if update.message else update.callback_query.from_user.id
        print(f"[DEBUG] Переход к состоянию '{state}' для пользователя {user_id}")

        # Находим конфигурацию состояния
        config = self.get_config_by_name(state)
        if not config:
            print(f"[ERROR] Конфигурация для состояния '{state}' не найдена.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return
        
        # Если это состояние для сбора никнейма, обработать его сразу
        if state == "username":
            username = update.message.from_user.username
            if username:  # Ник есть в Telegram
                self.user_storage.update_user(user_id, "username", username)
                await context.bot.send_message(chat_id=user_id, text=f"Твой ник @{username} сохранен автоматически.")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return
        
        if state == "other_education":
            user = self.user_storage.get_user(user_id)
            if user["education_choice"] != "Другое учебное заведение":
                self.user_storage.update_user(user_id, "other_education", "Нет")
                # await context.bot.send_message(chat_id=user_id, text="Другое учебное заведение заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return
            
        if state == "study_group":
            user = self.user_storage.get_user(user_id)
            if user["education_choice"] == "Закончил(а)" or user["education_choice"] == "Не учусь":
                self.user_storage.update_user(user_id, "study_group", "Нет")
                # await context.bot.send_message(chat_id=user_id, text="Учебную группу заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        if state == "rescheduling_session":
            user = self.user_storage.get_user(user_id)
            if user["education_choice"] == "Закончил(а)" or user["education_choice"] == "Не учусь":
                self.user_storage.update_user(user_id, "rescheduling_session", "Нет")
                # await context.bot.send_message(chat_id=user_id, text="Информацию про перенос сессии заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        if state == "rescheduling_practice":
            user = self.user_storage.get_user(user_id)
            if user["education_choice"] == "Закончил(а)" or user["education_choice"] == "Не учусь":
                self.user_storage.update_user(user_id, "rescheduling_practice", "Нет")
                # await context.bot.send_message(chat_id=user_id, text="Информацию про перенос практики заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        if state == "work_place":
            user = self.user_storage.get_user(user_id)
            if user["work"] == "Нет":
                self.user_storage.update_user(user_id, "work_place", user["work"])
                # await context.bot.send_message(chat_id=user_id, text="Место работы заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        # Сохраняем текущее состояние
        self.user_storage.update_state(user_id, state)

        # Генерируем сообщение состояния
        message = self.get_state_message(config, user_id)

        if "options" in config:
            reply_markup = self.create_inline_keyboard(
                config["options"],
                selected_options=[],
                multi_select=config.get("multi_select", False)
            )
        elif "buttons" in config:
            buttons = config["buttons"]() if callable(config["buttons"]) else config["buttons"]
            reply_markup = ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True)
        elif config.get("request_contact"):
            reply_markup = ReplyKeyboardMarkup(
                [[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]],
                resize_keyboard=True
            )
        else:
            reply_markup = ReplyKeyboardRemove()


        print(f"[DEBUG] Отправка сообщения пользователю {user_id}: {message}")
        await context.bot.send_message(chat_id=user_id, text=message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)

    async def handle_input(self, update, context):
        """Обрабатывает пользовательский ввод для всех состояний."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)
        current_state = user["state"]

        print(f"[DEBUG] Пользователь {user_id} находится в состоянии '{current_state}'")

        config = self.get_config_by_name(current_state)
        if not config:
            print(f"[ERROR] Некорректное состояние '{current_state}'")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        user_input = update.message.contact.phone_number if update.message.contact else update.message.text

        # Обработка выбора действия (edit, registered)
        if "buttons" in config:
            await self.process_action_input(update, context, user_input, current_state)
            return

        # Обработка ввода данных (регистрация/редактирование)
        await self.process_data_input(update, context, user_input, current_state)

    async def process_action_input(self, update, context, user_input, current_state):
        """Обрабатывает кнопки в состояниях registered и edit."""
        user_id = update.message.from_user.id

        if current_state == "registered" and user_input == "Изменить данные":
            print(f"[DEBUG] Пользователь {user_id} выбрал 'Изменить данные'.")
            await self.transition_state(update, context, "edit")
            return

        if current_state == "edit":
            if user_input == "Отмена":
                print(f"[DEBUG] Пользователь {user_id} отменил редактирование.")
                await self.transition_state(update, context, "registered")
                return

            field_config = self.get_config_by_label(user_input)
            if not field_config:
                print(f"[ERROR] Поле '{user_input}' не найдено.")
                await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
                return

            await self.transition_state(update, context, f"edit_{field_config['name']}")

    def apply_db_formatter(self, field_name, value):
        """Применяет форматтер для базы данных, если он указан в конфиге."""
        field_config = next((f for f in FIELDS if f["name"] == field_name), None)
        db_formatter = field_config.get("db_formatter")
        return db_formatter(value) if db_formatter else value

    async def process_data_input(self, update, context, user_input, field_name):
        """Обрабатывает пользовательский ввод, проверяет и форматирует перед сохранением."""
        user_id = update.effective_user.id

        # Убираем edit_, чтобы найти конфиг в FIELDS
        actual_field_name = field_name.replace("edit_", "")
        field_config = next((f for f in FIELDS if f["name"] == actual_field_name), None)

        if not field_config:
            print(f"[ERROR] Поле '{actual_field_name}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        # Если поле предполагает выбор из кнопок
        if field_config.get("options"):
            selected_options = self.user_storage.get_user(user_id).get(actual_field_name, "")
            selected_options = selected_options.split(", ") if selected_options else []
            if user_input == "Готово":
                if not selected_options:
                    await context.bot.send_message(chat_id=user_id, text="Выберите хотя бы один вариант.")
                    return
                formatted_db_value = ", ".join(selected_options)
                self.user_storage.update_user(user_id, actual_field_name, formatted_db_value)
                next_state = self.get_next_state(field_name)
                print(f"[DEBUG] Следующее состояние для пользователя {user_id}: {next_state}")
                await self.transition_state(update, context, next_state)
                return

            # Обновляем выбор
            if user_input in selected_options:
                selected_options.remove(user_input)
            else:
                selected_options.append(user_input)

            try:
                # Перерисовываем клавиатуру
                reply_markup = InlineKeyboardMarkup(
                    self.create_inline_keyboard(field_config["options"], selected_options)
                )
                await context.bot.edit_message_reply_markup(
                    chat_id=update.effective_chat.id,
                    message_id=update.effective_message.message_id,
                    reply_markup=reply_markup
                )
            except telegram.error.BadRequest as e:
                print(f"[ERROR] Не удалось отредактировать сообщение: {e}")
                # Уведомление пользователя или fallback действие
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Произошла ошибка при обновлении клавиатуры. Попробуйте ещё раз."
                )

        # Если поле требует номер телефона
        if field_config.get("request_contact") and update.message.contact:
            user_input = update.message.contact.phone_number

        # Проверяем валидатор, если указан
        if field_config.get("validator") and not field_config["validator"](user_input):
            await context.bot.send_message(chat_id=user_id, text=f"Некорректное значение для {field_config['label']}. Попробуй снова.")
            return

        # Форматируем и сохраняем данные
        formatted_db_value = self.apply_db_formatter(actual_field_name, user_input)
        self.user_storage.update_user(user_id, actual_field_name, formatted_db_value)

        # Переход к следующему состоянию
        next_state = self.get_next_state(field_name)
        await self.transition_state(update, context, next_state)

    def get_next_state(self, current_state):
        actual_state = current_state.replace("edit_", "")

        if current_state.startswith("edit_"):
            return "registered"  # Возврат к registered после редактирования

        if actual_state in self.steps:
            current_index = self.steps.index(actual_state)
            if current_index < len(self.steps) - 1:
                return self.steps[current_index + 1]
        return "registered"

    def get_config_by_name(self, state_name):
        """Возвращает конфигурацию состояния по имени."""
        print(f"[DEBUG] Поиск конфигурации для состояния '{state_name}'")

        if state_name.startswith("edit_"):
            original_field_name = state_name.replace("edit_", "")
            config = next((f for f in FIELDS if f["name"] == original_field_name), None)
            if config:
                print(f"[DEBUG] Сгенерирована конфигурация для edit состояния: {config}")
            else:
                print(f"[ERROR] Конфигурация для edit состояния '{state_name}' не найдена.")
            return config

        config = next((f for f in FIELDS if f["name"] == state_name), None) or self.states_config.get(state_name)
        if config:
            print(f"[DEBUG] Найдена конфигурация для состояния '{state_name}': {config}")
        else:
            print(f"[ERROR] Конфигурация для состояния '{state_name}' не найдена.")
        return config

    def get_config_by_label(self, label):
        """Возвращает конфигурацию поля по его label (используется в редактировании)."""
        return next((f for f in FIELDS if f["label"] == label), None)

    def format_input(self, field_config, user_input):
        """Форматирует данные, если у поля есть форматтер."""
        return field_config["formatter"](user_input) if "formatter" in field_config and callable(field_config["formatter"]) else user_input

    def apply_display_formatter(self, field_name, value):
        """Применяет форматтер для отображения, если он указан в конфиге."""
        field_config = next((f for f in FIELDS if f["name"] == field_name), None)
        display_formatter = field_config.get("display_formatter")
        return display_formatter(value) if display_formatter else value

    def get_state_message(self, config, user_id):
        """Формирует сообщение состояния, включая подстановку данных пользователя."""
        print(f"[DEBUG] Формирование сообщения для состояния '{config['name']}'")

        if config["name"] == "registered":
            user = self.user_storage.get_user(user_id)
            print(f"[DEBUG] Данные пользователя из базы: {user}")

            # Формируем словарь с данными пользователя
            user_data = {
                field["name"]: field["display_formatter"](user.get(field["name"], "Не указано"))
                if "display_formatter" in field and callable(field["display_formatter"])
                else user.get(field["name"], "Не указано")
                for field in FIELDS
            }

            print(f"[DEBUG] Подготовленные данные для подстановки: {user_data}")

            # Формируем сообщение с подстановкой данных
            return config["message"].format(**user_data)

        # Возвращаем стандартное сообщение для других состояний
        return config["message"]

    def create_reply_markup(self, config, selected_options=None):
        """Создает клавиатуру для состояния."""
        if "options" in config:
            return self.create_inline_keyboard(
                config["options"],
                selected_options=selected_options,
                multi_select=config.get("multi_select", False),
            )
        if "buttons" in config:
            buttons = self.create_buttons(config)
            return ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True) if buttons else ReplyKeyboardRemove()
        if config.get("request_contact"):
            return ReplyKeyboardMarkup([[KeyboardButton(text="Поделиться номером из Telegram", request_contact=True)]], resize_keyboard=True, one_time_keyboard=True)
        return ReplyKeyboardRemove()

    async def clear_inline_keyboard(self, update, context):
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
        current_state = user["state"]

        # Преобразование edit_* в основное имя поля
        actual_field_name = current_state.replace("edit_", "")

        # Проверяем, является ли выбор одиночным или множественным
        field_config = self.get_config_by_name(actual_field_name)
        is_multi_select = field_config.get("multi_select", False)

        if action == "select":
            selected_options = user.get(actual_field_name, "").split(", ") if user.get(actual_field_name) else []

            if is_multi_select:
                if option in selected_options:
                    selected_options.remove(option)  # Убираем, если уже выбрано
                else:
                    selected_options.append(option)  # Добавляем, если не выбрано
            else:
                selected_options = [option]  # Для одиночного выбора заменяем на текущий выбор

            # Обновляем выбранные значения в базе
            self.user_storage.update_user(user_id, actual_field_name, ", ".join(selected_options))

            # Формируем кнопки
            buttons = [
                InlineKeyboardButton(
                    f"✅ {opt}" if opt in selected_options else opt,
                    callback_data=f"select|{opt}"
                )
                for opt in field_config["options"]
            ]

            # Кнопки в две колонки
            buttons = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            buttons.append([InlineKeyboardButton("Готово", callback_data="done")])
            reply_markup = InlineKeyboardMarkup(buttons)

            await query.edit_message_reply_markup(reply_markup=reply_markup)

        elif action == "done":
            # Удаляем только клавиатуру
            await self.clear_inline_keyboard(update, context)

            # Определяем следующее состояние
            next_state = self.get_next_state(current_state)
            print(f"[DEBUG] Переход к следующему состоянию: {next_state}")

            # Переход к следующему состоянию
            await self.transition_state(update, context, next_state)


    def create_buttons(self, config):
        """Создает список кнопок."""
        buttons = config.get("buttons")
        return buttons() if callable(buttons) else buttons

    def get_config_by_name(self, state_name):
        """Возвращает конфигурацию состояния по имени."""
        print(f"[DEBUG] Поиск конфигурации для состояния '{state_name}'")

        # Проверяем, является ли это edit_ состояние
        if state_name.startswith("edit_"):
            original_field_name = state_name.replace("edit_", "")
            config = next((f for f in FIELDS if f["name"] == original_field_name), None)
            if config:
                print(f"[DEBUG] Сгенерирована конфигурация для edit состояния: {config}")
            else:
                print(f"[ERROR] Конфигурация для edit состояния '{state_name}' не найдена.")
            return config

        # Ищем конфигурацию в FIELDS или POST_REGISTRATION_STATES
        config = next((f for f in FIELDS if f["name"] == state_name), None) or self.states_config.get(state_name)
        if config:
            print(f"[DEBUG] Найдена конфигурация для состояния '{state_name}': {config}")
        else:
            print(f"[ERROR] Конфигурация для состояния '{state_name}' не найдена.")
        return config

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
            keyboard.append([InlineKeyboardButton("Готово", callback_data="done")])

        return InlineKeyboardMarkup(keyboard)  # Возвращаем объект InlineKeyboardMarkup


# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
