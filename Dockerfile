# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем оставшуюся часть исходного кода
COPY src/ ./src
COPY scenario.json ./
COPY .env ./

# Указываем команду для запуска приложения
CMD ["python", "src/main.py"]
