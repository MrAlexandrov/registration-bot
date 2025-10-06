# Используем базовый образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости и Poetry
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get remove -y curl && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# Настраиваем Poetry для работы в контейнере
RUN poetry config virtualenvs.create false

# Копируем файлы конфигурации Poetry
COPY pyproject.toml poetry.lock ./

# Устанавливаем зависимости (без dev-зависимостей для production)
RUN poetry install --only main --no-interaction --no-ansi

# Копируем весь проект в контейнер
COPY . .

# Определяем команду запуска бота
CMD ["python", "src/main.py"]
