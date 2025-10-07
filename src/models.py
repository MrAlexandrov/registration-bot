"""
SQLAlchemy ORM models for the registration bot.
Models are created dynamically based on SURVEY_CONFIG.
"""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# Create a separate base for dynamic model creation
DynamicBase = declarative_base()


def create_user_model(survey_config):
    """
    Dynamically create User model based on survey configuration.

    Args:
        survey_config: RegistrationSurveyConfig instance

    Returns:
        User model class with fields from survey_config
    """
    # Base attributes that every User model will have
    attrs = {
        "__tablename__": "users",
        "__table_args__": (
            Index("idx_user_telegram_id", "telegram_id"),
            Index("idx_user_state", "state"),
        ),
        # Base fields
        "id": Column(Integer, primary_key=True, autoincrement=True),
        "telegram_id": Column(Integer, unique=True, nullable=False, index=True),
        "state": Column(String, nullable=False),
        "is_blocked": Column(Integer, default=0, nullable=False),  # 0 = не заблокирован, 1 = заблокирован
        "created_at": Column(DateTime, default=datetime.utcnow, nullable=False),
        "updated_at": Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False),
    }

    # Add dynamic fields from survey config
    for field in survey_config.fields:
        field_name = field.field_name
        db_type = getattr(field, "db_type", "TEXT").upper()

        # Map db_type to SQLAlchemy column type
        if db_type == "INTEGER":
            col_type = Integer
        elif db_type == "DATETIME":
            col_type = DateTime
        else:  # TEXT or any other type defaults to Text
            col_type = Text

        attrs[field_name] = Column(col_type, nullable=True)
        logger.debug(f"Added field '{field_name}' with type {col_type.__name__} to User model")

    # Add methods to the class
    def __repr__(self) -> str:
        return f"<User(telegram_id={self.telegram_id}, state='{self.state}')>"

    def to_dict(self) -> dict[str, Any]:
        """Convert user object to dictionary."""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            else:
                result[column.name] = value
        return result

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        """Create user object from dictionary."""
        valid_keys = {column.name for column in cls.__table__.columns}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)

    def update_from_dict(self, data: dict[str, Any]) -> None:
        """Update user fields from dictionary."""
        valid_keys = {column.name for column in self.__table__.columns}
        for key, value in data.items():
            if key in valid_keys and key not in ["id", "created_at"]:
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()

    attrs["__repr__"] = __repr__
    attrs["to_dict"] = to_dict
    attrs["from_dict"] = from_dict
    attrs["update_from_dict"] = update_from_dict

    # Create the User class dynamically
    User = type("User", (DynamicBase,), attrs)

    logger.info(f"Created User model with {len(survey_config.fields)} dynamic fields")
    return User


# User model will be initialized after importing SURVEY_CONFIG
User = None


def initialize_models():
    """
    Initialize models based on SURVEY_CONFIG.
    This should be called after SURVEY_CONFIG is loaded.
    """
    global User

    try:
        from .settings import SURVEY_CONFIG

        User = create_user_model(SURVEY_CONFIG)
        logger.info("User model initialized successfully")
        return User
    except ImportError as e:
        logger.error(f"Could not import SURVEY_CONFIG: {e}")
        raise


def get_user_model():
    """
    Get the User model, initializing it if necessary.

    Returns:
        User model class
    """
    global User
    if User is None:
        User = initialize_models()
    return User
