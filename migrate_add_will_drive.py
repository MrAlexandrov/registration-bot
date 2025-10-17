#!/usr/bin/env python3
"""
Скрипт миграции для добавления поля will_drive в базу данных.

Добавляет колонку will_drive и заполняет её значением по умолчанию "Не смогу 😢"
для всех существующих пользователей.

Использование:
    python3 migrate_add_will_drive.py [--dry-run]
"""

import sqlite3
import sys
from pathlib import Path


DEFAULT = "Жду ответа по этому году ❗"

def migrate_add_will_drive(db_path, default_value=DEFAULT, dry_run=False):
    """
    Добавляет колонку will_drive в таблицу users.
    
    Args:
        db_path: Путь к базе данных
        default_value: Значение по умолчанию для существующих пользователей
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
        
        # Проверяем, существует ли уже колонка will_drive
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'will_drive' in columns:
            print("⚠️  Колонка 'will_drive' уже существует в таблице users")
            print("   Миграция не требуется")
            conn.close()
            return True
        
        # Получаем количество пользователей
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        print(f"\n📊 Найдено пользователей в БД: {user_count}")
        
        if dry_run:
            print("\n🔍 [DRY RUN] Будут выполнены следующие действия:")
            print(f"   1. Добавлена колонка 'will_drive' типа TEXT")
            print(f"   2. Для {user_count} пользователей установлено значение: '{default_value}'")
        else:
            # Добавляем колонку will_drive
            print(f"\n➕ Добавляем колонку 'will_drive'...")
            cursor.execute("""
                ALTER TABLE users 
                ADD COLUMN will_drive TEXT
            """)
            print("✅ Колонка 'will_drive' добавлена")
            
            # Заполняем значением по умолчанию для всех существующих пользователей
            if user_count > 0:
                print(f"\n📝 Заполняем значением по умолчанию: '{default_value}'...")
                cursor.execute("""
                    UPDATE users 
                    SET will_drive = ?
                    WHERE will_drive IS NULL
                """, (default_value,))
                
                updated_count = cursor.rowcount
                print(f"✅ Обновлено записей: {updated_count}")
            
            # Сохраняем изменения
            conn.commit()
            print("\n💾 Изменения сохранены в базу данных")
        
        # Закрываем соединение
        conn.close()
        
        # Выводим итоги
        print("\n" + "="*60)
        print("📊 ИТОГИ МИГРАЦИИ:")
        print(f"   Пользователей в БД: {user_count}")
        print(f"   Колонка 'will_drive': {'будет добавлена' if dry_run else 'добавлена'}")
        print(f"   Значение по умолчанию: '{default_value}'")
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
    print("🔄 МИГРАЦИЯ: ДОБАВЛЕНИЕ ПОЛЯ will_drive")
    print("="*60)
    
    # Путь к базе данных
    db_path = "data/database.sqlite"
    
    # Значение по умолчанию (из messages.py)
    default_value = DEFAULT
    
    # Проверяем аргументы командной строки
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("\n⚠️  Режим пробного запуска (dry run) - изменения не будут сохранены")
    
    print(f"\n📁 База данных: {db_path}")
    print(f"📝 Значение по умолчанию: '{default_value}'")
    
    # Запускаем миграцию
    success = migrate_add_will_drive(db_path, default_value, dry_run=dry_run)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()