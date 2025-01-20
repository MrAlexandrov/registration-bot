from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext
from user_storage import user_storage
from settings import FIELDS, POST_REGISTRATION_STATES


class RegistrationFlow:
    def __init__(self, user_storage):
        self.user_storage = user_storage
        self.steps = [field["name"] for field in FIELDS]

    async def handle_command(self, update, context):
        """Обрабатывает команды, такие как /start."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)

        if not user:
            print(f"[DEBUG] Создание нового пользователя {user_id}")
            self.user_storage.create_user(user_id)
            await self.transition_state(update, context, self.steps[0])
        else:
            current_state = user["state"]
            print(f"[DEBUG] Пользователь {user_id} уже существует в состоянии '{current_state}'")

            if current_state == "registered":
                # Если пользователь уже зарегистрирован, показываем меню
                await self.transition_state(update, context, "registered")
            else:
                # Если пользователь в процессе регистрации, продолжаем с текущего состояния
                await self.transition_state(update, context, current_state)

    async def transition_state(self, update, context, state):
        """Переход в указанное состояние."""
        user_id = update.message.from_user.id
        print(f"[DEBUG] Переход к состоянию '{state}' для пользователя {user_id}")

        # Если состояние после регистрации
        if state in POST_REGISTRATION_STATES:
            config = POST_REGISTRATION_STATES[state]
            print(f"[DEBUG] Пользователь {user_id} переходит в состояние '{state}' после регистрации.")
            self.user_storage.update_state(user_id, state)

            # Подставляем данные пользователя в сообщение
            if state == "registered":
                user = self.user_storage.get_user(user_id)
                message = config["message"].format(
                    name=user.get("name", "Не указано"),
                    phone=user.get("phone", "Не указано"),
                    email=user.get("email", "Не указано"),
                    age=user.get("age", "Не указано")
                )
            else:
                message = config["message"]

            # Генерация кнопок
            if "buttons" in config:
                buttons = config["buttons"]
                if callable(buttons):  # Если это функция
                    buttons = buttons()

                reply_markup = ReplyKeyboardMarkup(
                    [[button] for button in buttons],
                    resize_keyboard=True
                )
            else:
                reply_markup = None

            await context.bot.send_message(
                chat_id=user_id,
                text=message,
                reply_markup=reply_markup
            )
            return

        # Обработка стандартных состояний регистрации
        field_config = next((f for f in FIELDS if f["name"] == state), None)
        if not field_config:
            print(f"[ERROR] Состояние '{state}' не найдено.")
            await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
            return

        print(f"[DEBUG] Задаём вопрос '{field_config['question']}' для пользователя {user_id}")
        self.user_storage.update_state(user_id, state)
        await context.bot.send_message(chat_id=user_id, text=field_config["question"])

    async def handle_input(self, update, context):
        """Обрабатывает пользовательский ввод."""
        user_id = update.message.from_user.id
        user = self.user_storage.get_user(user_id)
        current_state = user["state"]

        # Лог текущего состояния
        print(f"[DEBUG] Пользователь {user_id} находится в состоянии '{current_state}'")

        # Обработка состояния 'registered'
        if current_state == "registered":
            user_input = update.message.text
            config = POST_REGISTRATION_STATES.get(current_state)

            if not config or "buttons" not in config:
                print(f"[ERROR] Нет конфигурации для состояния 'registered' или кнопок.")
                await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
                return

            # Проверяем, какая кнопка была нажата
            if user_input == "Изменить данные":
                print(f"[DEBUG] Пользователь {user_id} выбрал 'Изменить данные'.")
                await self.transition_state(update, context, "edit")
                return

            print(f"[ERROR] Некорректный ввод '{user_input}' в состоянии 'registered'.")
            await context.bot.send_message(chat_id=user_id, text="Пожалуйста, выбери действие из предложенных.")
            return

        # Обработка состояния 'edit'
        if current_state == "edit":
            field_label = update.message.text
            if field_label == "Отмена":
                print(f"[DEBUG] Пользователь {user_id} отменил редактирование.")
                await self.transition_state(update, context, "registered")
                return

            # Определяем следующее состояние
            field_config = next((f for f in FIELDS if f["label"] == field_label), None)
            if not field_config:
                print(f"[ERROR] Поле с меткой '{field_label}' не найдено.")
                await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
                return

            next_state = f"edit_{field_config['name']}"
            print(f"[DEBUG] Переход к состоянию '{next_state}' для пользователя {user_id}")
            await self.transition_state(update, context, next_state)
            return

        # Обработка изменения конкретного поля
        if current_state.startswith("edit_"):
            field_name = current_state.replace("edit_", "")
            field_config = next((f for f in FIELDS if f["name"] == field_name), None)
            if not field_config:
                print(f"[ERROR] Поле '{field_name}' не найдено.")
                await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
                return

            user_input = update.message.text
            if "validator" in field_config:
                is_valid = field_config["validator"](user_input)
                if not is_valid:
                    print(f"[DEBUG] Некорректное значение '{user_input}' для поля '{field_name}'")
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"Некорректное значение для {field_config['label']}. Попробуй снова."
                    )
                    return

            # Форматируем и сохраняем данные
            value = field_config["formatter"](user_input) if "formatter" in field_config and callable(
                field_config["formatter"]) else user_input
            self.user_storage.update_user(user_id, field_name, value)
            print(f"[DEBUG] Сохранён ответ '{value}' для поля '{field_name}'")

            # Возвращаемся в состояние 'registered'
            next_state = POST_REGISTRATION_STATES[current_state]["next_state"]
            await self.transition_state(update, context, next_state)
            return

        # Обработка стандартных состояний
        if current_state in self.steps:
            field_config = next((f for f in FIELDS if f["name"] == current_state), None)
            if not field_config:
                print(f"[ERROR] Поле '{current_state}' не найдено в FIELDS.")
                await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")
                return

            user_input = update.message.text
            if "validator" in field_config:
                is_valid = field_config["validator"](user_input)
                if not is_valid:
                    print(f"[DEBUG] Некорректное значение '{user_input}' для поля '{current_state}'")
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"Некорректное значение для {field_config['label']}. Попробуй снова."
                    )
                    return

            # Форматируем и сохраняем данные
            value = field_config["formatter"](user_input) if "formatter" in field_config and callable(
                field_config["formatter"]) else user_input
            self.user_storage.update_user(user_id, current_state, value)
            print(f"[DEBUG] Сохранён ответ '{value}' для поля '{current_state}'")

            # Переход к следующему состоянию
            next_index = self.steps.index(current_state) + 1
            if next_index < len(self.steps):
                next_state = self.steps[next_index]
                await self.transition_state(update, context, next_state)
            else:
                await self.transition_state(update, context, "registered")
            return

        print(f"[ERROR] Некорректное текущее состояние '{current_state}' для пользователя {user_id}.")
        await context.bot.send_message(chat_id=user_id, text="Произошла ошибка. Попробуй снова.")


# Инициализируем регистрацию
registration_flow = RegistrationFlow(user_storage)
