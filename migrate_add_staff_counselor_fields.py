#!/usr/bin/env python3
"""
Migration script to add is_staff and is_counselor fields to existing users table.

This script adds two new fields to the users table:
- is_staff: INTEGER (0 or 1) - indicates if user is a staff member (organizer)
- is_counselor: INTEGER (0 or 1) - indicates if user is a counselor

Usage:
    python migrate_add_staff_counselor_fields.py [--db-path PATH]

Options:
    --db-path PATH    Path to database file (default: data/database.sqlite)
"""

import argparse
import logging
import sqlite3
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def check_column_exists(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    """Check if a column exists in a table."""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def add_staff_counselor_fields(db_path: str) -> None:
    """
    Add is_staff and is_counselor fields to users table.
    
    Args:
        db_path: Path to SQLite database file
    """
    if not Path(db_path).exists():
        logger.error(f"Database file not found: {db_path}")
        sys.exit(1)

    logger.info(f"Opening database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            logger.error("Users table not found in database")
            sys.exit(1)
        
        # Check and add is_staff field
        if check_column_exists(cursor, "users", "is_staff"):
            logger.info("Column 'is_staff' already exists, skipping")
        else:
            logger.info("Adding 'is_staff' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_staff INTEGER DEFAULT 0 NOT NULL")
            logger.info("✅ Added 'is_staff' column")
        
        # Check and add is_counselor field
        if check_column_exists(cursor, "users", "is_counselor"):
            logger.info("Column 'is_counselor' already exists, skipping")
        else:
            logger.info("Adding 'is_counselor' column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN is_counselor INTEGER DEFAULT 0 NOT NULL")
            logger.info("✅ Added 'is_counselor' column")
        
        # Create indexes for the new fields
        logger.info("Creating indexes for new fields...")
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_is_staff ON users(is_staff)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_is_counselor ON users(is_counselor)")
            logger.info("✅ Created indexes")
        except sqlite3.OperationalError as e:
            logger.warning(f"Index creation warning (may already exist): {e}")
        
        # Commit changes
        conn.commit()
        
        # Verify the changes
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        logger.info("\nCurrent users table structure:")
        for col in columns:
            logger.info(f"  - {col[1]} ({col[2]})")
        
        # Count users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        logger.info(f"\n✅ Migration completed successfully!")
        logger.info(f"Total users in database: {user_count}")
        logger.info(f"All users have is_staff=0 and is_counselor=0 by default")
        logger.info(f"\nTo update these fields:")
        logger.info(f"1. Use /register_staff_chat in your staff chat")
        logger.info(f"2. Use /register_counselor_chat in your counselor chat")
        logger.info(f"3. Bot will automatically update fields when users join/leave these chats")
        
        conn.close()
        
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Add is_staff and is_counselor fields to users table"
    )
    parser.add_argument(
        "--db-path",
        default="data/database.sqlite",
        help="Path to database file (default: data/database.sqlite)",
    )
    
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("Migration: Add is_staff and is_counselor fields")
    logger.info("=" * 60)
    
    add_staff_counselor_fields(args.db_path)


if __name__ == "__main__":
    main()