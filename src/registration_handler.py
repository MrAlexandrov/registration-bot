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

    async def try_auto_collect_nickname(self, update, context, state, user_id):
        username = update.message.from_user.username
        if username:  # Ник есть в Telegram
            self.user_storage.update_user(user_id, "username", username)
            await context.bot.send_message(chat_id=user_id, text=f"Твой ник @{username} сохранен автоматически.")
            next_state = self.get_next_state(state)
            await self.transition_state(update, context, next_state)
            return True
        return False

    async def try_skip_education_questions(self, update, context, state, user_id, user_data):
        if state == "other_education":
            if user_data["education_choice"] != "Другое учебное заведение":
                self.user_storage.update_user(user_id, "other_education", "Нет")
                # await context.bot.send_message(chat_id=user_id, text="Другое учебное заведение заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return True

        if state == "study_group":
            if user_data["education_choice"] == "Закончил(а)" or user_data["education_choice"] == "Не учусь":
                self.user_storage.update_user(user_id, "study_group", "Нет")
                # await context.bot.send_message(chat_id=user_id, text="Учебную группу заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return True

        if state == "rescheduling_session":
            if user_data["education_choice"] == "Закончил(а)" or user_data["education_choice"] == "Не учусь":
                self.user_storage.update_user(user_id, "rescheduling_session", "Нет")
                # await context.bot.send_message(chat_id=user_id, text="Информацию про перенос сессии заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return True

        if state == "rescheduling_practice":
            if user_data["education_choice"] == "Закончил(а)" or user_data["education_choice"] == "Не учусь":
                self.user_storage.update_user(user_id, "rescheduling_practice", "Нет")
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
            print(f"[ERROR] Конфигурация для состояния '{state}' не найдена.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return
        
        # Если это состояние для сбора никнейма, обработать его сразу
        if state == "username":
            if await self.try_auto_collect_nickname(update, context, state, user_id):
                return

        if state in {"other_education", "study_group", "rescheduling_session", "rescheduling_practice"}:
            if await self.try_skip_education_questions(update, context, state, user_id, user_data):
                return

        if state == "work_place":
            if user_data["work"] == "Нет":
                self.user_storage.update_user(user_id, "work_place", user_data["work"])
                # await context.bot.send_message(chat_id=user_id, text="Место работы заполнять не нужно")
                next_state = self.get_next_state(state)
                await self.transition_state(update, context, next_state)
                return

        # Сохраняем текущее состояние
        self.user_storage.update_state(user_id, state)

        # Генерируем сообщение состояния
        message = self.get_state_message(config, user_id)

        actual_field_name = state.replace("edit_", "")
        if "options" in config:
            selected_options = user_data.get(actual_field_name, "")
            selected_options = selected_options.split(", ") if selected_options else []
            reply_markup = self.create_inline_keyboard(
                config["options"],
                selected_options=selected_options,
                multi_select=config.get("multi_select", False)
            )
        elif "buttons" in config:
            buttons = config["buttons"]() if callable(config["buttons"]) else config["buttons"]

            if state == "edit":
                user_nickname = user_data.get("username", "")

                # Убираем кнопку "Изменить ник", если ник уже установлен
                if user_nickname:
                    buttons = [button for button in buttons if button != "Никнейм"]

            reply_markup = ReplyKeyboardMarkup([[button] for button in buttons], resize_keyboard=True)
        elif config.get("request_contact"):
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
        current_state = user["state"]

        print(f"[DEBUG] Пользователь {user_id} находится в состоянии '{current_state}'")

        config = self.get_config_by_state(current_state)
        if not config:
            print(f"[ERROR] Некорректное состояние '{current_state}'")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        user_input = update.message.contact.phone_number if update.message.contact else update.message.text

        # Обработка выбора действия (edit, registered)
        if "buttons" in config:
            await self.process_action_input(update, context, current_state, user_input)
            return

        # Обработка ввода данных (регистрация/редактирование)
        await self.process_data_input(update, context, current_state, user_input)

    async def process_action_input(self, update, context, state, user_input):
        """Обрабатывает кнопки в состояниях registered и edit."""
        user_id = update.message.from_user.id

        if state == "registered" and user_input == "Изменить данные":
            print(f"[DEBUG] Пользователь {user_id} выбрал 'Изменить данные'.")
            await self.transition_state(update, context, "edit")
            return

        if state == "edit":
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

    async def process_data_input(self, update, context, state, user_input):
        """Обрабатывает пользовательский ввод, проверяет и форматирует перед сохранением."""
        print("******************************************************** process_data_input")
        user_id = update.effective_user.id
        user_data = self.user_storage.get_user(user_id)

        # Убираем edit_, чтобы найти конфиг в FIELDS
        actual_state = state.replace("edit_", "")
        field_config = next((f for f in FIELDS if f["name"] == actual_state), None)

        if not field_config:
            print(f"[ERROR] Поле '{actual_state}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        # Если поле требует номер телефона
        if field_config.get("request_contact") and update.message.contact:
            user_input = update.message.contact.phone_number

        # Проверяем валидатор, если указан
        if field_config.get("validator") and not field_config["validator"](user_input):
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
            return "registered"  # Возврат к registered после редактирования

        if actual_state in self.steps:
            current_index = self.steps.index(actual_state)
            if current_index < len(self.steps) - 1:
                return self.steps[current_index + 1]

        return "registered"

    def get_config_by_state(self, state):
        """Возвращает конфигурацию состояния по имени."""
        print(f"[DEBUG] Поиск конфигурации для состояния '{state}'")

        if state.startswith("edit_"):
            original_field_name = state.replace("edit_", "")
            config = next((f for f in FIELDS if f["name"] == original_field_name), None)
            if config:
                print(f"[DEBUG] Сгенерирована конфигурация для edit состояния: {config}")
            else:
                print(f"[ERROR] Конфигурация для edit состояния '{state}' не найдена.")
            return config

        config = next((f for f in FIELDS if f["name"] == state), None) or self.states_config.get(state)
        if config:
            print(f"[DEBUG] Найдена конфигурация для состояния '{state}': {config}")
        else:
            print(f"[ERROR] Конфигурация для состояния '{state}' не найдена.")
        return config

    def get_config_by_label(self, label):
        """Возвращает конфигурацию поля по его label (используется в редактировании)."""
        return next((f for f in FIELDS if f["label"] == label), None)

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
        state = user["state"]

        # Преобразование edit_* в основное имя поля
        actual_field_name = state.replace("edit_", "")

        # Проверяем, является ли выбор одиночным или множественным
        field_config = self.get_config_by_state(actual_field_name)
        is_multi_select = field_config.get("multi_select", False)

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
                for opt in field_config["options"]
            ]

            # Кнопки в две колонки
            buttons = [buttons[i:i + 2] for i in range(0, len(buttons), 2)]
            buttons.append([InlineKeyboardButton("Готово", callback_data="done")])
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
            keyboard.append([InlineKeyboardButton("Готово", callback_data="done")])

        return InlineKeyboardMarkup(keyboard)  # Возвращаем объект InlineKeyboardMarkup


# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
