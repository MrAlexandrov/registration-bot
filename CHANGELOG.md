# Changelog - Система прав доступа

## Исправления (2025-10-07)

### Исправлена проблема с определением блокировки бота

**Проблема:** Бот путал удаление из группового чата с блокировкой пользователем.

**Решение:** Добавлена проверка типа чата. Теперь [`track_chat_member_updates()`](src/main.py:38) обрабатывает только приватные чаты:

```python
# Обрабатываем только приватные чаты (блокировка/разблокировка бота)
if chat.type != "private":
    logger.debug(f"Ignoring chat member update in non-private chat {chat.id}")
    return
```

### Исправлена работа команд в групповых чатах

**Проблема:** Команды не работали в групповых чатах.

**Решения:**

1. **Обработка команд с упоминанием бота:** В [`handle_admin_command()`](src/admin_commands.py:20) добавлена обработка команд вида `/command@botname`:
   ```python
   # Remove bot username if present (e.g., /command@botname -> /command)
   command = command_text.split('@')[0]
   ```

2. **Разделение обработчиков по типу чата:**
   - Административные команды работают в любых чатах
   - Команды регистрации работают только в приватных чатах
   ```python
   # Registration commands - only in private chats
   application.add_handler(CommandHandler("start", start, filters=filters.ChatType.PRIVATE))
   ```

### Автоматическая инициализация ROOT пользователя

**Добавлено:** Функция [`post_init()`](src/main.py:79) автоматически выдаёт все права ROOT пользователю при запуске бота:

```python
async def post_init(application):
    """Initialize bot after startup - grant ROOT user admin permissions."""
    # Grant all permissions to ROOT user
    permissions_to_grant = [
        Permission.ADMIN,
        Permission.TABLE_VIEWER,
        Permission.MESSAGE_SENDER,
        Permission.STAFF
    ]
```

Теперь ROOT пользователь автоматически получает все права при первом запуске бота.

## Как это работает теперь

### Блокировка бота
- ✅ Блокировка в приватном чате → `is_blocked = 1`
- ✅ Разблокировка в приватном чате → `is_blocked = 0`
- ✅ Удаление из группового чата → игнорируется
- ✅ Добавление в групповой чат → игнорируется

### Команды в чатах
- ✅ Административные команды работают везде (приватные чаты и группы)
- ✅ Команды регистрации работают только в приватных чатах
- ✅ Поддержка команд с упоминанием бота: `/command@botname`

### Инициализация ROOT
- ✅ При запуске бота ROOT автоматически получает все права
- ✅ Права записываются в базу данных
- ✅ Повторный запуск не создаёт дубликаты

## Тестирование

Для проверки исправлений:

1. **Тест блокировки:**
   ```bash
   # В приватном чате сботом
   /start  # Зарегистрироваться
   # Заблокировать бота → должно залогироваться "User X blocked the bot"
   # Разблокировать бота → должно залогироваться "User X unblocked the bot"
   ```

2. **Тест команд в группе:**
   ```bash
   # В групповом чате
   /my_permissions  # Должно работать
   /my_permissions@your_bot_name  # Должно работать
   ```

3. **Тест ROOT инициализации:**
   ```bash
   # Запустить бота
   make run
   # В логах должно быть:
   # "Initializing ROOT user permissions..."
   # "Granted admin to ROOT user X"
   # "ROOT user initialization complete"

   # Проверить права
   /my_permissions  # Должны быть все права
   ```

## Обновление

Для применения исправлений:

```bash
# Остановить бота (Ctrl+C)
# Перезапустить
make run
```

Изменения применятся автоматически. База данных не требует миграции.