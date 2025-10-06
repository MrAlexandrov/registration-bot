"""
Тесты для форматтеров - обновлены для новой системы.
"""
import pytest
from src.survey.formatters import (
    format_phone_db,
    format_phone_display,
    format_date_db,
    format_username_display,
    format_text_db,
    format_default_display
)


@pytest.mark.parametrize("phone, expected", [
    ("89991234567", "79991234567"),
    ("+79991234567", "79991234567"),
    ("79991234567", "79991234567"),
    ("8 (999) 123-45-67", "79991234567"),
])
def test_format_phone_db(phone, expected):
    assert format_phone_db(phone) == expected


@pytest.mark.parametrize("phone, expected", [
    ("79991234567", "+79991234567"),
    ("", "Не указан"),
])
def test_format_phone_display(phone, expected):
    assert format_phone_display(phone) == expected


@pytest.mark.parametrize("date, expected", [
    ("1.1.2020", "01.01.2020"),
    ("10.12.1995", "10.12.1995"),
    ("31.12.2023", "31.12.2023"),
])
def test_format_date_db(date, expected):
    assert format_date_db(date) == expected


@pytest.mark.parametrize("username, expected", [
    ("testuser", "@testuser"),
    ("", "Не указан"),
])
def test_format_username_display(username, expected):
    assert format_username_display(username) == expected


@pytest.mark.parametrize("text, expected", [
    ("  Hello World  ", "Hello World"),
    ("Test", "Test"),
    ("", ""),
])
def test_format_text_db(text, expected):
    assert format_text_db(text) == expected


@pytest.mark.parametrize("value, expected", [
    ("Test Value", "Test Value"),
    ("", "Не указано"),
    (None, "Не указано"),
])
def test_format_default_display(value, expected):
    result = format_default_display(value or "")
    assert result == expected
