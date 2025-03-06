#!/bin/bash

ROOT_DIRECTORY="$HOME/registration-bot"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
echo "Dump started at ${TIMESTAMP}" | tee -a "${ROOT_DIRECTORY}/debug.log"

# Путь к вашей базе данных
DATABASE_PATH="${ROOT_DIRECTORY}/database.sqlite"
SOURCE_LOG="${ROOT_DIRECTORY}/screenlog.0"

# Директория для хранения дампов
DUMP_DIR="${ROOT_DIRECTORY}/dumps"

# Убедиться, что директория для дампов существует
mkdir -p "$DUMP_DIR"
if [ $? -ne 0 ]; then
    echo "Ошибка создания директории $DUMP_DIR" | tee -a "${ROOT_DIRECTORY}/debug.log"
    exit 1
fi

# Генерация уникального имени с использованием метки времени
DUMP_NAME="dump_$TIMESTAMP.sqlite"
DUMP_PATH="$DUMP_DIR/$DUMP_NAME"

# Копирование базы данных
if ! cp "$DATABASE_PATH" "$DUMP_PATH"; then
    echo "Ошибка при копировании базы данных" | tee -a "${ROOT_DIRECTORY}/debug.log"
else
    echo "База данных сохранена в $DUMP_PATH" | tee -a "${ROOT_DIRECTORY}/debug.log"
    sudo chattr +i "$DUMP_PATH"
fi

# Копирование логов
if [ -f "$SOURCE_LOG" ]; then
    if cp "$SOURCE_LOG" "$DUMP_DIR/screenlog_$TIMESTAMP.log"; then
        rm "$SOURCE_LOG"
        echo "Лог сохранён в $DUMP_DIR/screenlog_$TIMESTAMP.log" | tee -a "${ROOT_DIRECTORY}/debug.log"
        sudo chattr +i "$DUMP_DIR/screenlog_$TIMESTAMP.log"
    else
        echo "Ошибка при копировании лога $SOURCE_LOG" | tee -a "${ROOT_DIRECTORY}/debug.log"
    fi
else
    echo "Файл $SOURCE_LOG не найден" | tee -a "${ROOT_DIRECTORY}/debug.log"
fi
