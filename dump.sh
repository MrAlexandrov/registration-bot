#!/bin/bash

# Скрипт для резервного копирования базы данных SQLite
# Использование: ./dump.sh

# Получаем директорию, где находится скрипт
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Путь к базе данных (относительно директории проекта)
DATABASE_PATH="$SCRIPT_DIR/data/database.sqlite"

# Директория для хранения дампов
DUMP_DIR="$SCRIPT_DIR/dumps"

# Максимальное количество хранимых дампов (удаляем старые)
MAX_BACKUPS=168  # 7 дней * 24 часа = 168 резервных копий

# Убедиться, что директория для дампов существует
mkdir -p "$DUMP_DIR"

# Проверить, существует ли база данных
if [ ! -f "$DATABASE_PATH" ]; then
    echo "❌ Ошибка: База данных не найдена по пути: $DATABASE_PATH"
    exit 1
fi

# Генерация уникального имени с использованием метки времени
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DUMP_NAME="dump_$TIMESTAMP.sqlite"
DUMP_PATH="$DUMP_DIR/$DUMP_NAME"

# Копирование базы данных
cp "$DATABASE_PATH" "$DUMP_PATH"

# Проверить успешность копирования
if [ $? -eq 0 ]; then
    echo "✅ База данных сохранена как $DUMP_PATH"
    
    # Получить размер файла
    SIZE=$(du -h "$DUMP_PATH" | cut -f1)
    echo "📦 Размер резервной копии: $SIZE"
    
    # Удалить старые дампы, оставив только последние MAX_BACKUPS
    BACKUP_COUNT=$(ls -1 "$DUMP_DIR"/dump_*.sqlite 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt "$MAX_BACKUPS" ]; then
        echo "🗑️  Удаление старых резервных копий (оставляем последние $MAX_BACKUPS)..."
        ls -1t "$DUMP_DIR"/dump_*.sqlite | tail -n +$((MAX_BACKUPS + 1)) | xargs rm -f
        echo "✅ Старые резервные копии удалены"
    fi
    
    # Показать общее количество резервных копий
    TOTAL_BACKUPS=$(ls -1 "$DUMP_DIR"/dump_*.sqlite 2>/dev/null | wc -l)
    echo "📊 Всего резервных копий: $TOTAL_BACKUPS"
else
    echo "❌ Ошибка при создании резервной копии"
    exit 1
fi
