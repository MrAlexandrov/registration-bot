"""
Тесты для валидаторов - обновлены для новой системы.
"""

import pytest

from src.survey.validators import (
    create_options_validator,
    validate_date,
    validate_email,
    validate_non_empty,
    validate_phone,
    validate_yes_no,
)


@pytest.mark.parametrize(
    "date, is_valid",
    [
        ("01.01.2000", True),
        ("31.12.1999", True),
        ("15.06.2007", True),
        ("1.1.2008", True),
        ("2000-01-01", False),
        ("32.12.2010", False),
        ("abc", False),
        ("", False),
    ],
)
def test_validate_date(date, is_valid):
    valid, _ = validate_date(date)
    assert valid == is_valid


@pytest.mark.parametrize(
    "phone, is_valid",
    [
        ("+79998887766", True),
        ("89998887766", True),
        ("79998887766", True),
        ("8 (999) 888-77-66", True),
        ("9998887766", False),
        ("abc", False),
        ("", False),
    ],
)
def test_validate_phone(phone, is_valid):
    valid, _ = validate_phone(phone)
    assert valid == is_valid


@pytest.mark.parametrize(
    "email, is_valid",
    [
        ("test@example.com", True),
        ("test.test@example.co.uk", True),
        ("test@example", False),
        ("test", False),
        ("", False),
    ],
)
def test_validate_email(email, is_valid):
    valid, _ = validate_email(email)
    assert valid == is_valid


@pytest.mark.parametrize(
    "text, is_valid",
    [
        ("Hello", True),
        ("  Hello  ", True),
        ("", False),
        ("   ", False),
    ],
)
def test_validate_non_empty(text, is_valid):
    valid, _ = validate_non_empty(text)
    assert valid == is_valid


@pytest.mark.parametrize(
    "value, is_valid",
    [
        ("Да", True),
        ("Нет", True),
        ("Maybe", False),
        ("", False),
    ],
)
def test_validate_yes_no(value, is_valid):
    valid, _ = validate_yes_no(value)
    assert valid == is_valid


def test_create_options_validator():
    """Тест создания валидатора опций."""
    options = ["Вариант1", "Вариант2", "Вариант3"]
    validator = create_options_validator(options)

    # Валидные опции
    valid, _ = validator("Вариант1")
    assert valid is True

    valid, _ = validator("Вариант2")
    assert valid is True

    # Невалидная опция
    valid, _ = validator("НесуществующийВариант")
    assert valid is False
