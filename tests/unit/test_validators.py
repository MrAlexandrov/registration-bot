import pytest
import os
from validators import (
    validate_date,
    validate_phone,
    validate_email,
    validate_probability
)

# Универсальная функция для загрузки тестовых данных
def load_test_data(valid_filename, invalid_filename):
    base_path = os.path.join(os.path.dirname(__file__), "data")

    def read_data(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return [line.strip() for line in file if line.strip()]  # Убираем пустые строки

    valid_data = [(item, True) for item in read_data(os.path.join(base_path, valid_filename))]
    invalid_data = [(item, False) for item in read_data(os.path.join(base_path, invalid_filename))]

    return valid_data + invalid_data  # Объединяем в один список

# ✅ Фикстура с путями к файлам (кеширует данные в pytest)
@pytest.fixture(scope="module")
def test_data():
    return {
        "dates": load_test_data("valid_dates.txt", "invalid_dates.txt"),
        "phones": load_test_data("valid_phones.txt", "invalid_phones.txt"),
        "emails": load_test_data("valid_emails.txt", "invalid_emails.txt"),
        "probabilities": [
            ("0", True), ("50", True), ("100", True),
            ("-1", False), ("101", False), ("abc", False),
        ],
    }

@pytest.mark.parametrize("date, expected", load_test_data("valid_dates.txt", "invalid_dates.txt"))
def test_validate_date(date, expected):
    assert validate_date(date) == expected

@pytest.mark.parametrize("phone, expected", load_test_data("valid_phones.txt", "invalid_phones.txt"))
def test_validate_phone(phone, expected):
    assert validate_phone(phone) == expected

@pytest.mark.parametrize("email, expected", load_test_data("valid_emails.txt", "invalid_emails.txt"))
def test_validate_email(email, expected):
    assert validate_email(email) == expected

@pytest.mark.parametrize("probability, expected", [
    ("0", True), ("50", True), ("100", True),
    ("-1", False), ("101", False), ("abc", False),
])
def test_validate_probability(probability, expected):
    assert validate_probability(probability) == expected
