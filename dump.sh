#!/bin/bash

# Путь к вашей базе данных
DATABASE_PATH="database.sqlite"

# Директория для хранения дампов
DUMP_DIR="dumps"

# Убедиться, что директория для дампов существует
mkdir -p $DUMP_DIR

# Генерация уникального имени с использованием метки времени
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_NAME="dump_$TIMESTAMP.sqlite"
DUMP_PATH="$DUMP_DIR/$DUMP_NAME"

# Копирование базы данных
cp "$DATABASE_PATH" "$DUMP_PATH"

echo "База данных сохранена как $DUMP_PATH"
