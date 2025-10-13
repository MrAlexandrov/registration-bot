# Логирование сообщений

## Описание

Система автоматического логирования всех сообщений, которыми обмениваются пользователи и бот. Все сообщения сохраняются в базе данных для последующего анализа и коммуникации с зарегистрированными пользователями.

## Структура базы данных

### Таблица `messages`

Хранит все входящие и исходящие сообщения.

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | INTEGER | Первичный ключ (автоинкремент) |
| `telegram_id` | BIGINT | Telegram ID пользователя |
| `chat_id` | BIGINT | ID чата (обычно совпадает с telegram_id для личных чатов) |
| `message_id` | BIGINT | ID сообщения в Telegram |
| `direction` | VARCHAR(10) | Направление: 'incoming' (от пользователя) или 'outgoing' (от бота) |
| `message_type` | VARCHAR(50) | Тип сообщения: 'text', 'photo', 'document', 'contact' и т.д. |
| `text` | TEXT | Текст сообщения |
| `caption` | TEXT | Подпись к медиа-файлам |
| `file_id` | VARCHAR(255) | Telegram file_id для медиа-файлов |
| `reply_to_message_id` | BIGINT | ID сообщения, на которое отвечают |
| `created_at` | DATETIME | Время создания записи |

### Индексы

Для оптимизации запросов созданы следующие индексы:
- `idx_message_telegram_id` - по telegram_id
- `idx_message_chat_id` - по chat_id
- `idx_message_direction` - по направлению сообщения
- `idx_message_created_at` - по времени создания

## Использование

### Автоматическое логирование

Логирование происходит автоматически:

1. **Входящие сообщения** - логируются в обработчике [`handle_message()`](src/main.py:33) в [`main.py`](src/main.py:1)
2. **Исходящие сообщения** - логируются в [`MessageSender.send_message()`](src/message_sender.py:39) в [`message_sender.py`](src/message_sender.py:1)

### Программное использование

```python
from src.message_logger import message_logger

# Получить последние 100 сообщений пользователя
messages = message_logger.get_user_messages(
    telegram_id=12345,
    limit=100
)

# Получить только входящие сообщения
incoming = message_logger.get_user_messages(
    telegram_id=12345,
    direction="incoming",
    limit=50
)

# Получить только исходящие сообщения
outgoing = message_logger.get_user_messages(
    telegram_id=12345,
    direction="outgoing",
    limit=50
)
```

### Прямой доступ к базе данных

```python
from src.database import db
from src.models import Message

with db.get_session() as session:
    # Получить все сообщения пользователя
    messages = session.query(Message).filter(
        Message.telegram_id == 12345
    ).order_by(Message.created_at.desc()).all()
    
    # Получить статистику по типам сообщений
    from sqlalchemy import func
    stats = session.query(
        Message.message_type,
        func.count(Message.id)
    ).group_by(Message.message_type).all()
```

## Компоненты системы

### 1. Модель данных ([`src/models.py`](src/models.py:1))

Класс [`Message`](src/models.py:19) - ORM модель для таблицы сообщений.

### 2. Логгер сообщений ([`src/message_logger.py`](src/message_logger.py:1))

Класс [`MessageLogger`](src/message_logger.py:18) предоставляет методы:
- [`log_incoming_message(update)`](src/message_logger.py:20) - логирование входящих сообщений
- [`log_outgoing_message(telegram_id, chat_id, sent_message, ...)`](src/message_logger.py:73) - логирование исходящих сообщений
- [`get_user_messages(telegram_id, limit, direction)`](src/message_logger.py:157) - получение сообщений пользователя
- [`_get_message_type(message)`](src/message_logger.py:180) - определение типа сообщения

### 3. Интеграция

- **Входящие сообщения**: интегрировано в [`handle_message()`](src/main.py:33) в [`src/main.py`](src/main.py:1)
- **Исходящие сообщения**: интегрировано в [`MessageSender.send_message()`](src/message_sender.py:39) в [`src/message_sender.py`](src/message_sender.py:1)

## Инициализация

Таблица `messages` создаётся автоматически при запуске бота через [`UserStorage._create_table()`](src/user_storage.py:44), которая вызывает [`db.create_tables()`](src/database.py:53).

## Типы сообщений

Поддерживаются следующие типы сообщений:
- `text` - текстовые сообщения
- `photo` - фотографии
- `document` - документы
- `video` - видео
- `audio` - аудио
- `voice` - голосовые сообщения
- `sticker` - стикеры
- `contact` - контакты
- `location` - геолокация
- `poll` - опросы
- `other` - другие типы

## Примеры использования

### Анализ переписки с пользователем

```python
from src.message_logger import message_logger

# Получить всю историю переписки
messages = message_logger.get_user_messages(telegram_id=12345, limit=1000)

# Вывести последние 10 сообщений
for msg in messages[:10]:
    direction = "→" if msg.direction == "outgoing" else "←"
    print(f"{direction} [{msg.created_at}] {msg.text}")
```

### Поиск сообщений по содержимому

```python
from src.database import db
from src.models import Message

with db.get_session() as session:
    # Найти все сообщения содержащие определённый текст
    messages = session.query(Message).filter(
        Message.text.like('%регистрация%')
    ).all()
```

### Статистика по пользователю

```python
from src.database import db
from src.models import Message
from sqlalchemy import func

with db.get_session() as session:
    # Количество сообщений от пользователя
    incoming_count = session.query(func.count(Message.id)).filter(
        Message.telegram_id == 12345,
        Message.direction == "incoming"
    ).scalar()
    
    # Количество сообщений от бота
    outgoing_count = session.query(func.count(Message.id)).filter(
        Message.telegram_id == 12345,
        Message.direction == "outgoing"
    ).scalar()
    
    print(f"От пользователя: {incoming_count}")
    print(f"От бота: {outgoing_count}")
```

## Производительность

- Все операции логирования выполняются асинхронно и не блокируют основной поток бота
- Ошибки логирования не влияют на работу бота (логируются, но не прерывают выполнение)
- Индексы обеспечивают быструю выборку сообщений по пользователю и времени

## Конфиденциальность

⚠️ **Важно**: Все сообщения пользователей сохраняются в базе данных. Убедитесь, что:
- База данных защищена от несанкционированного доступа
- Соблюдаются требования законодательства о защите персональных данных
- Пользователи проинформированы о сохранении их сообщений