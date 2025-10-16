#!/usr/bin/env python3
"""
Скрипт миграции пользователей из старой базы данных в новую.

Старая БД: data/users.db
Новая БД: data/database.sqlite

Использование:
    python3 migrate_users.py
"""

import re
import sqlite3
import sys
from datetime import datetime, UTC
from pathlib import Path


def parse_timestamp(timestamp_str):
    """
    Парсит timestamp из старой БД в datetime объект.
    Поддерживает различные форматы.
    """
    if not timestamp_str:
        return datetime.now(UTC)
    
    # Попробуем разные форматы
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",  # 2024-01-15 10:30:45.123456
        "%Y-%m-%d %H:%M:%S",      # 2024-01-15 10:30:45
        "%Y-%m-%d",               # 2024-01-15
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(timestamp_str, fmt)
            # Добавляем timezone info
            return dt.replace(tzinfo=UTC)
        except ValueError:
            continue
    
    # Если не удалось распарсить, возвращаем текущее время
    print(f"⚠️  Не удалось распарсить timestamp: {timestamp_str}, используем текущее время")
    return datetime.now(UTC)


def format_phone_db(value: str) -> str:
    """
    Форматирует телефон для сохранения в БД.
    Удаляет все символы кроме цифр и заменяет 8 на 7 в начале.
    """
    # Удаляем все символы кроме цифр
    phone = re.sub(r"\D", "", str(value))
    
    # Заменяем 8 на 7 в начале
    if phone.startswith("8"):
        phone = "7" + phone[1:]
    
    return phone


def migrate_users(old_db_path, new_db_path, dry_run=False):
    """
    Мигрирует пользователей из старой БД в новую.
    
    Args:
        old_db_path: Путь к старой БД (users.db)
        new_db_path: Путь к новой БД (database.sqlite)
        dry_run: Если True, только показывает что будет сделано без изменений
    """
    # Проверяем существование файлов
    if not Path(old_db_path).exists():
        print(f"❌ Старая база данных не найдена: {old_db_path}")
        return False
    
    if not Path(new_db_path).exists():
        print(f"❌ Новая база данных не найдена: {new_db_path}")
        print("   Сначала запустите бота, чтобы создать новую БД")
        return False
    
    try:
        # Подключаемся к обеим БД
        old_conn = sqlite3.connect(old_db_path)
        old_conn.row_factory = sqlite3.Row
        old_cursor = old_conn.cursor()
        
        new_conn = sqlite3.connect(new_db_path)
        new_cursor = new_conn.cursor()
        
        # Получаем всех пользователей из старой БД
        old_cursor.execute("SELECT * FROM users")
        old_users = old_cursor.fetchall()
        
        print(f"\n📊 Найдено пользователей в старой БД: {len(old_users)}")
        
        if len(old_users) == 0:
            print("⚠️  Нет пользователей для миграции")
            return True
        
        # Проверяем, какие пользователи уже есть в новой БД
        new_cursor.execute("SELECT telegram_id FROM users")
        existing_telegram_ids = {row[0] for row in new_cursor.fetchall()}
        
        print(f"📊 Пользователей уже в новой БД: {len(existing_telegram_ids)}")
        
        migrated_count = 0
        skipped_count = 0
        error_count = 0
        
        for old_user in old_users:
            telegram_id = old_user['user_id']
            
            # Пропускаем, если пользователь уже есть в новой БД
            if telegram_id in existing_telegram_ids:
                print(f"⏭️  Пропускаем пользователя {telegram_id} (уже существует)")
                skipped_count += 1
                continue
            
            try:
                # Парсим timestamp
                created_at = parse_timestamp(old_user['timestamp'])
                
                # Подготавливаем данные для вставки
                new_user_data = {
                    'telegram_id': telegram_id,
                    'state': 'registered',  # Все старые пользователи считаются зарегистрированными
                    'is_blocked': 0,
                    'created_at': created_at,
                    'updated_at': created_at,
                    'username': old_user['username'],
                    'telegram_sername': None,  # Новое поле, оставляем пустым
                    'name': old_user['full_name'],
                    'birth_date': old_user['birth_date'],
                    'group': old_user['study_group'],
                    'phone': format_phone_db(old_user['phone_number']),
                    'expectations': old_user['expectations'],
                }
                
                if dry_run:
                    print(f"\n🔍 [DRY RUN] Будет мигрирован пользователь {telegram_id}:")
                    print(f"   Username: {new_user_data['username']}")
                    print(f"   Full name: {new_user_data['telegram_sername']}")
                    print(f"   Birth date: {new_user_data['birth_date']}")
                    print(f"   Group: {new_user_data['group']}")
                    print(f"   Phone: {new_user_data['phone']}")
                else:
                    # Вставляем пользователя в новую БД
                    new_cursor.execute("""
                        INSERT INTO users (
                            telegram_id, state, is_blocked, created_at, updated_at,
                            username, telegram_sername, name, birth_date, "group", phone, expectations
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        new_user_data['telegram_id'],
                        new_user_data['state'],
                        new_user_data['is_blocked'],
                        new_user_data['created_at'],
                        new_user_data['updated_at'],
                        new_user_data['username'],
                        new_user_data['telegram_sername'],
                        new_user_data['name'],
                        new_user_data['birth_date'],
                        new_user_data['group'],
                        new_user_data['phone'],
                        new_user_data['expectations'],
                    ))
                    
                    print(f"✅ Мигрирован пользователь {telegram_id} (@{new_user_data['username']})")
                
                migrated_count += 1
                
            except Exception as e:
                print(f"❌ Ошибка при миграции пользователя {telegram_id}: {e}")
                error_count += 1
                continue
        
        if not dry_run:
            new_conn.commit()
        
        # Закрываем соединения
        old_conn.close()
        new_conn.close()
        
        # Выводим итоги
        print("\n" + "="*60)
        print("📊 ИТОГИ МИГРАЦИИ:")
        print(f"   Всего пользователей в старой БД: {len(old_users)}")
        print(f"   Мигрировано: {migrated_count}")
        print(f"   Пропущено (уже существуют): {skipped_count}")
        print(f"   Ошибок: {error_count}")
        print("="*60)
        
        if dry_run:
            print("\n⚠️  Это был пробный запуск (dry run).")
            print("   Для реальной миграции запустите без параметра --dry-run")
        else:
            print("\n✅ Миграция завершена успешно!")
        
        return error_count == 0
        
    except Exception as e:
        print(f"\n❌ Критическая ошибка при миграции: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Главная функция скрипта."""
    print("="*60)
    print("🔄 МИГРАЦИЯ ПОЛЬЗОВАТЕЛЕЙ")
    print("="*60)
    
    # Пути к базам данных
    old_db_path = "data/users.db"
    new_db_path = "data/database.sqlite"
    
    # Проверяем аргументы командной строки
    dry_run = "--dry-run" in sys.argv
    
    if dry_run:
        print("\n⚠️  Режим пробного запуска (dry run) - изменения не будут сохранены")
    
    # Запускаем миграцию
    success = migrate_users(old_db_path, new_db_path, dry_run=dry_run)
    
    if success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()