import pytest
from formatters import format_phone_db, format_phone_display, format_date, format_probability_display

@pytest.mark.parametrize("phone, expected", [
    ("89991234567", "79991234567"),
    ("+79991234567", "79991234567"),
    ("79991234567", "79991234567"),
])
def test_format_phone_db(phone, expected):
    assert format_phone_db(phone) == expected

@pytest.mark.parametrize("phone, expected", [
    ("79991234567", "+79991234567"),
])
def test_format_phone_display(phone, expected):
    assert format_phone_display(phone) == expected

@pytest.mark.parametrize("date, expected", [
    ("1.1.2020", "01.01.2020"),
    ("10.12.1995", "10.12.1995"),
])
def test_format_date(date, expected):
    assert format_date(date) == expected

@pytest.mark.parametrize("probability, expected", [
    ("10", "10%"),
    ("100", "100%"),
])
def test_format_probability_display(probability, expected):
    assert format_probability_display(probability) == expected
