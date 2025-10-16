#!/bin/bash

# Скрипт для настройки автоматического резервного копирования через cron
# Создаёт задачу cron для запуска dump.sh каждый час

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "Настройка автоматического резервного копирования"
echo "================================================"
echo ""

# Получаем абсолютный путь к директории проекта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DUMP_SCRIPT="$SCRIPT_DIR/dump.sh"

# Проверяем, существует ли dump.sh
if [ ! -f "$DUMP_SCRIPT" ]; then
    echo -e "${RED}❌ Ошибка: Файл dump.sh не найден по пути: $DUMP_SCRIPT${NC}"
    exit 1
fi

# Делаем dump.sh исполняемым
chmod +x "$DUMP_SCRIPT"
echo -e "${GREEN}✅ Файл dump.sh сделан исполняемым${NC}"

# Создаём директорию для логов
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/backup.log"

echo -e "${GREEN}✅ Директория для логов создана: $LOG_DIR${NC}"

# Формируем задачу cron (каждый час)
CRON_JOB="0 * * * * $DUMP_SCRIPT >> $LOG_FILE 2>&1"

# Проверяем, существует ли уже такая задача
if crontab -l 2>/dev/null | grep -q "$DUMP_SCRIPT"; then
    echo -e "${YELLOW}⚠️  Задача cron для резервного копирования уже существует${NC}"
    echo ""
    echo "Текущие задачи cron:"
    crontab -l | grep "$DUMP_SCRIPT"
    echo ""
    read -p "Хотите обновить задачу? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Отменено пользователем"
        exit 0
    fi
    
    # Удаляем старую задачу
    crontab -l | grep -v "$DUMP_SCRIPT" | crontab -
    echo -e "${GREEN}✅ Старая задача удалена${NC}"
fi

# Добавляем новую задачу cron
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

# Проверяем успешность добавления
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ Задача cron успешно добавлена!${NC}"
    echo ""
    echo "📋 Детали задачи:"
    echo "   Расписание: Каждый час (в начале часа)"
    echo "   Скрипт: $DUMP_SCRIPT"
    echo "   Лог: $LOG_FILE"
    echo ""
    echo "📊 Текущие задачи cron:"
    crontab -l | grep "$DUMP_SCRIPT"
    echo ""
    echo -e "${YELLOW}💡 Полезные команды:${NC}"
    echo "   Просмотреть все задачи cron:  crontab -l"
    echo "   Редактировать задачи cron:    crontab -e"
    echo "   Удалить все задачи cron:      crontab -r"
    echo "   Просмотреть логи:             tail -f $LOG_FILE"
    echo ""
    echo -e "${GREEN}✅ Настройка завершена!${NC}"
    echo ""
    echo "Резервные копии будут создаваться каждый час и сохраняться в директорию:"
    echo "$SCRIPT_DIR/dumps"
    echo ""
    echo "Старые резервные копии (старше 7 дней) будут автоматически удаляться."
else
    echo -e "${RED}❌ Ошибка при добавлении задачи cron${NC}"
    exit 1
fi