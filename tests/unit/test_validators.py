import pytest
import os
from validators import (
    validate_date,
    validate_phone,
    validate_email,
    validate_probability
)

@pytest.mark.parametrize("date, is_valid", [
    ("01.01.2000", True),
    ("31.12.1999", True),
    ("15.06.2023", True),
    ("2000-01-01", False),
    ("32.12.2022", False),
    ("abc", False),
])
def test_validate_date(date, is_valid):
    valid, _ = validate_date(date)
    assert valid == is_valid


@pytest.mark.parametrize("phone, is_valid", [
    ("+79998887766", True),
    ("89998887766", True),
    ("79998887766", True),
    ("9998887766", False),
    ("abc", False),
])
def test_validate_phone(phone, is_valid):
    valid, _ = validate_phone(phone)
    assert valid == is_valid


@pytest.mark.parametrize("email, is_valid", [
    ("test@example.com", True),
    ("test.test@example.co.uk", True),
    ("test@example", False),
    ("test", False),
])
def test_validate_email(email, is_valid):
    valid, _ = validate_email(email)
    assert valid == is_valid


@pytest.mark.parametrize("probability, is_valid", [
    ("0", True), ("50", True), ("100", True),
    ("-1", False), ("101", False), ("abc", False),
])
def test_validate_probability(probability, is_valid):
    valid, _ = validate_probability(probability)
    assert valid == is_valid
