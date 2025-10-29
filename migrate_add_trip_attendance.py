#!/usr/bin/env python3
"""
Скрипт миграции для добавления поля trip_attendance в базу данных.

Добавляет колонку trip_attendance для хранения ответов на опрос о выезде.
Значение по умолчанию NULL (опрос ещё не пройден).

Использование:
    python3 migrate_add_trip_attendance.py [--dry-run]
"""

import sqlite3
import sys
from pathlib import Path


def migrate_add_trip_attendance(db_path, dry_run=False):
    """
    Добавляет колонку trip_attendance в таблицу users.
    
    Args:
        db_path: Путь к базе данных
        dry_run: Если True, только показывает что будет сделано без изменений
    """
    # Проверяем существование файла
    if not Path(db_path).exists():
        print(f"❌ База данных не найдена: {db_path}")
        print("   Сначала запустите бота, чтобы создать БД")
        return False
    
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Проверяем, существует ли уже колонка trip_attendance
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'trip_attendance' in columns:
            print("⚠️  Колонка 'trip_attendance' уже существует в таблице users")
            print("   Миграция не требуется")
            conn.close()
            return True
        
        # Получаем количество пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        print(f"\n📊 Найдено пользователей в БД: {user_count}")
        
        if dry_run:
            print("\n🔍 [DRY RUN] Будут выполнены следующие действия:")
            print(f"   1. Добавлена колонка 'trip_attendance' типа TEXT")
            print(f"   2. Для всех пользователей значение будет NULL (опрос не пройден)")
        else:
            # Добавляем колонку trip_attendance
            print(f"\n➕ Добавляем колонку 'trip_attendance'...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN trip_attendance TEXT
            """)
            print("✅ Колонка 'trip_attendance' добавлена")
            
            # Сохраняем изменения
            conn.commit()
            print("\n💾 Изменения сохранены в базу данных")
        
        # Закрываем соединение
        conn.close()
        
        # Выводим итоги
        print("\n" + "="*60)
        print("📊 ИТОГИ МИГРАЦИИ:")
        print(f"   Пользователей в БД: {user_count}")
        print(f"   Колонка 'trip_attendance': {'будет добавлена' if dry_run else 'добавлена'}")
        print(f"   Значение по умолчанию: NULL (опрос не пройден)")
        print("="*60)
        
        if dry_run:
            print("\n⚠️  Это был пробный запуск (dry run).")
            print("   Для реальной миграции запустите без параметра --dry-run")
        else:
            print("\n✅ Миграция завершена успешно!")
            print("\n💡 Рекомендация: Перезапустите бота, чтобы изменения вступили в силу")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при миграции: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция скрипта."""
    print("="*60)
    print("🔄 МИГРАЦИЯ: ДОБАВЛЕНИЕ ПОЛЯ trip_attendance")
    print("="*60)
    
    # Путь к базе данных
    db_path = "data/database.sqlite"
    
    # Проверяем аргументы командной строки
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("\n⚠️  Режим пробного запуска (dry run) - изменения не будут сохранены")
    
    print(f"\n📁 База данных: {db_path}")
    
    # Запускаем миграцию
    success = migrate_add_trip_attendance(db_path, dry_run=dry_run)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()