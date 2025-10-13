"""
Database configuration and session management for SQLAlchemy ORM.
"""

import logging
import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

logger = logging.getLogger(__name__)


class Database:
    """Database manager for SQLAlchemy ORM."""

    def __init__(self, db_path: str = "data/database.sqlite"):
        """
        Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.db_url = f"sqlite:///{db_path}"

        # Create engine with appropriate settings for SQLite
        self.engine = create_engine(
            self.db_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,  # Use StaticPool for SQLite
            echo=False,  # Set to True for SQL query logging
        )

        # Enable foreign keys for SQLite
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        logger.info(f"Database initialized at {db_path}")

    def create_tables(self):
        """Create all tables defined in models."""
        from .models import DynamicBase, Message, get_user_model

        # Ensure User model is initialized
        get_user_model()

        # Create all tables (including Message table)
        DynamicBase.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully (including messages table)")

    def drop_tables(self):
        """Drop all tables (use with caution!)."""
        from .models import DynamicBase

        DynamicBase.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Yields:
            Session: SQLAlchemy session

        Example:
            with db.get_session() as session:
                user = session.query(User).first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_new_session(self) -> Session:
        """
        Get a new database session (must be closed manually).

        Returns:
            Session: SQLAlchemy session

        Note:
            Remember to close the session when done:
            session = db.get_new_session()
            try:
                # ... use session
            finally:
                session.close()
        """
        return self.SessionLocal()


# Global database instance
db = Database()
