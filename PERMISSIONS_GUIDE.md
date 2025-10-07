# Руководство по системе прав доступа

## Обзор

Бот теперь использует гибкую систему управления правами доступа. Вместо жёсткого указания ID пользователей в `.env`, теперь достаточно указать только `ROOT_ID` (суперпользователя), который может управлять правами всех остальных пользователей.

## Основные концепции

### ROOT пользователь
- Указывается в `.env` как `ROOT_ID`
- Имеет все права автоматически
- Может управлять правами других пользователей
- Может регистрировать чаты

### Права доступа (Permissions)

1. **admin** - Управление пользователями и правами
   - Может выдавать и отзывать права других пользователей
   - Может просматривать списки пользователей с правами

2. **table_viewer** - Просмотр таблиц регистрации
   - Может получать таблицы с данными зарегистрированных пользователей

3. **message_sender** - Отправка сообщений
   - Может отправлять сообщения зарегистрированным пользователям

4. **staff** - Статус организатора
   - Автоматически выдаётся участникам чата организаторов
   - Может использоваться для предоставления дополнительного доступа

### Чаты

1. **Чат организаторов (staff chat)**
   - Регистрируется командой `/register_staff_chat`
   - Все участники автоматически получают право `staff`
   - При выходе из чата право `staff` автоматически отзывается

2. **Чат суперпользователей (superuser chat)**
   - Регистрируется командой `/register_superuser_chat`
   - Используется для уведомлений об ошибках
   - Может использоваться для других системных уведомлений

## Команды управления

### Управление правами

```bash
# Выдать право пользователю
/grant_permission <user_id> <permission>

# Примеры:
/grant_permission 123456789 admin
/grant_permission 987654321 table_viewer
/grant_permission 111222333 message_sender
/grant_permission 444555666 staff

# Отозвать право у пользователя
/revoke_permission <user_id> <permission>

# Пример:
/revoke_permission 123456789 admin

# Показать права конкретного пользователя
/list_permissions <user_id>

# Пример:
/list_permissions 123456789

# Показать всех пользователей с определённым правом
/list_users <permission>

# Примеры:
/list_users admin
/list_users table_viewer

# Показать ваши собственные права
/my_permissions
```

### Регистрация чатов (только ROOT)

```bash
# Зарегистрировать текущий чат как чат организаторов
# Выполняется в групповом чате
/register_staff_chat

# Зарегистрировать текущий чат для уведомлений об ошибках
# Выполняется в групповом чате
/register_superuser_chat
```

## Примеры использования

### Начальная настройка

1. Запустите бота с указанным `ROOT_ID` в `.env`
2. Создайте групповой чат для организаторов
3. Добавьте бота в этот чат
4. От имени ROOT пользователя выполните в чате:
   ```
   /register_staff_chat
   ```
5. Создайте групповой чат для уведомлений об ошибках
6. Добавьте бота в этот чат
7. От имени ROOT пользователя выполните в чате:
   ```
   /register_superuser_chat
   ```

### Выдача прав администратора

```bash
# ROOT выдаёт право admin пользователю
/grant_permission 123456789 admin

# Теперь этот пользователь может управлять правами других
```

### Настройка доступа к таблицам

```bash
# Выдать право просмотра таблиц нескольким пользователям
/grant_permission 111111111 table_viewer
/grant_permission 222222222 table_viewer
/grant_permission 333333333 table_viewer

# Проверить, кто может просматривать таблицы
/list_users table_viewer
```

### Управление организаторами

Организаторы управляются автоматически через чат:
1. Добавьте пользователя в чат организаторов → он получает право `staff`
2. Удалите пользователя из чата → право `staff` автоматически отзывается

Также можно выдать право `staff` вручную:
```bash
/grant_permission 123456789 staff
```

## Использование в коде

### Проверка прав в обработчиках

```python
from src.permission_helpers import require_permission, Permission

@require_permission(Permission.TABLE_VIEWER)
async def get_table(update, context):
    # Этот обработчик доступен только пользователям с правом table_viewer
    # Код обработчика
    pass

@require_permission(Permission.ADMIN)
async def manage_users(update, context):
    # Этот обработчик доступен только администраторам
    pass

@require_staff()
async def staff_only_command(update, context):
    # Этот обработчик доступен только организаторам
    pass

@require_root()
async def root_only_command(update, context):
    # Этот обработчик доступен только ROOT пользователю
    pass
```

### Проверка прав напрямую

```python
from src.permission_helpers import can_view_tables, can_send_messages, is_staff

user_id = update.effective_user.id

if can_view_tables(user_id):
    # Пользователь может просматривать таблицы
    pass

if can_send_messages(user_id):
    # Пользователь может отправлять сообщения
    pass

if is_staff(user_id):
    # Пользователь является организатором
    pass
```

### Отправка уведомлений об ошибках

```python
from src.error_notifier import error_notifier

try:
    # Ваш код
    pass
except Exception as e:
    # Отправить уведомление об ошибке в чат суперпользователей
    await error_notifier.notify_error(context, e, update)
```

### Отправка информационных уведомлений

```python
from src.error_notifier import error_notifier

# Отправить информационное сообщение в чат суперпользователей
await error_notifier.notify_info(
    context,
    "Новая регистрация",
    f"Зарегистрировался пользователь {user_id}"
)
```

## Миграция со старой системы

Если вы использовали `ADMIN_IDS` и `TABLE_GETTERS` в `.env`:

1. Оставьте только `ROOT_ID` в `.env`
2. Удалите или закомментируйте `ADMIN_IDS` и `TABLE_GETTERS`
3. Выдайте права пользователям через команды:
   ```bash
   # Вместо ADMIN_IDS=123,456,789
   /grant_permission 123 admin
   /grant_permission 456 admin
   /grant_permission 789 admin

   # Вместо TABLE_GETTERS=111,222,333
   /grant_permission 111 table_viewer
   /grant_permission 222 table_viewer
   /grant_permission 333 table_viewer
   ```

## База данных

Система прав использует две таблицы:

1. **user_permissions** - хранит права пользователей
   - `telegram_id` - ID пользователя
   - `permission` - название права
   - `granted_by` - кто выдал право
   - `created_at` - когда выдано

2. **bot_chats** - хранит зарегистрированные чаты
   - `chat_id` - ID чата
   - `chat_type` - тип чата (staff, superuser)
   - `chat_title` - название чата
   - `is_active` - активен ли чат

Таблицы создаются автоматически при первом запуске бота.

## Безопасность

- ROOT пользователь не может быть лишён прав
- Только ROOT и пользователи с правом `admin` могут управлять правами
- Только ROOT может регистрировать чаты
- Все действия логируются
- Ошибки автоматически отправляются в чат суперпользователей

## Расширение системы

Чтобы добавить новое право:

1. Добавьте его в `Permission` enum в `src/permissions.py`:
   ```python
   class Permission(str, Enum):
       # Существующие права
       ADMIN = "admin"
       # ...

       # Новое право
       MY_NEW_PERMISSION = "my_new_permission"
   ```

2. Используйте его в коде:
   ```python
   from src.permission_helpers import require_permission, Permission

   @require_permission(Permission.MY_NEW_PERMISSION)
   async def my_handler(update, context):
       pass
   ```

3. Выдавайте его пользователям:
   ```bash
   /grant_permission 123456789 my_new_permission