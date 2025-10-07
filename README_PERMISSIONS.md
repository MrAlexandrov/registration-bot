# Система прав доступа - Краткое руководство

## Быстрый старт

### 1. Настройка .env

Теперь достаточно указать только ROOT_ID:

```env
BOT_TOKEN=your_bot_token
ROOT_ID=your_telegram_id
```

Старые параметры `ADMIN_IDS` и `TABLE_GETTERS` больше не нужны!

### 2. Запуск бота

```bash
python -m src.main
```

### 3. Настройка чатов (от имени ROOT)

**Чат организаторов:**
1. Создайте групповой чат
2. Добавьте бота в чат
3. Выполните в чате: `/register_staff_chat`

**Чат для уведомлений об ошибках:**
1. Создайте групповой чат
2. Добавьте бота в чат
3. Выполните в чате: `/register_superuser_chat`

### 4. Выдача прав пользователям

```bash
# Сделать пользователя администратором
/grant_permission 123456789 admin

# Дать право просмотра таблиц
/grant_permission 987654321 table_viewer

# Дать право отправки сообщений
/grant_permission 111222333 message_sender

# Вручную выдать статус организатора
/grant_permission 444555666 staff
```

## Доступные права

| Право | Описание |
|-------|----------|
| `admin` | Управление пользователями и правами |
| `table_viewer` | Просмотр таблиц регистрации |
| `message_sender` | Отправка сообщений пользователям |
| `staff` | Статус организатора (автоматически из чата) |

## Основные команды

```bash
# Управление правами
/grant_permission <user_id> <permission>    # Выдать право
/revoke_permission <user_id> <permission>   # Отозвать право
/list_permissions <user_id>                 # Показать права пользователя
/list_users <permission>                    # Показать пользователей с правом
/my_permissions                             # Показать ваши права

# Регистрация чатов (только ROOT)
/register_staff_chat                        # Зарегистрировать чат организаторов
/register_superuser_chat                    # Зарегистрировать чат для ошибок
```

## Автоматическое управление организаторами

Участники чата организаторов автоматически получают право `staff`:
- ✅ Добавили в чат → получил право `staff`
- ❌ Удалили из чата → право `staff` отозвано

## Уведомления об ошибках

Все ошибки автоматически отправляются в чат суперпользователей с подробной информацией:
- Тип ошибки
- Сообщение об ошибке
- Информация о пользователе
- Traceback

## Использование в коде

### Проверка прав через декораторы

```python
from src.permission_helpers import require_permission, Permission

@require_permission(Permission.TABLE_VIEWER)
async def get_table(update, context):
    # Доступно только пользователям с правом table_viewer
    pass

@require_staff()
async def staff_command(update, context):
    # Доступно только организаторам
    pass
```

### Проверка прав напрямую

```python
from src.permission_helpers import can_view_tables, is_staff

if can_view_tables(user_id):
    # Отправить таблицу
    pass

if is_staff(user_id):
    # Показать дополнительные опции
    pass
```

### Отправка уведомлений

```python
from src.error_notifier import error_notifier

# Уведомление об ошибке
await error_notifier.notify_error(context, exception, update)

# Информационное уведомление
await error_notifier.notify_info(
    context,
    "Заголовок",
    "Текст сообщения"
)
```

## Миграция со старой системы

Если у вас были настроены `ADMIN_IDS` и `TABLE_GETTERS`:

1. Удалите их из `.env`
2. Оставьте только `ROOT_ID`
3. Выдайте права через команды:

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

## Преимущества новой системы

✅ **Гибкость** - можно выдавать разные права разным пользователям
✅ **Масштабируемость** - легко добавлять новые права
✅ **Удобство** - управление через команды бота, не нужно редактировать .env
✅ **Автоматизация** - организаторы управляются через чат
✅ **Мониторинг** - автоматические уведомления об ошибках
✅ **Безопасность** - все действия логируются

## Подробная документация

Полное руководство: [`PERMISSIONS_GUIDE.md`](PERMISSIONS_GUIDE.md)

## Тестирование

```bash
# Запустить тесты системы прав
python -m pytest tests/test_permissions.py -v
```

## Структура файлов

```
src/
├── permissions.py          # Основная система прав
├── admin_commands.py       # Команды управления
├── chat_tracker.py         # Отслеживание чатов
├── error_notifier.py       # Уведомления об ошибках
└── permission_helpers.py   # Вспомогательные функции

tests/
└── test_permissions.py     # Тесты системы прав

PERMISSIONS_GUIDE.md        # Подробное руководство
README_PERMISSIONS.md       # Это файл (краткое руководство)