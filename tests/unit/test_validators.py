import pytest
import os
from validators import validate_group, validate_date, validate_phone


# Универсальная функция для чтения данных из файла
def read_data_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = [line.strip() for line in file if line.strip()]  # Убираем пустые строки
    return data

# Универсальная функция для параметризации тестов
def parametrize_data(file_path, expected_result):
    data = read_data_from_file(file_path)
    return [(item, expected_result) for item in data]

# Пути к файлам с данными для групп
valid_groups_file_path = os.path.join(os.path.dirname(__file__), './data/valid_groups.txt')
invalid_groups_file_path = os.path.join(os.path.dirname(__file__), './data/invalid_groups.txt')

# Получение данных для групп
valid_groups_data = parametrize_data(valid_groups_file_path, True)
invalid_groups_data = parametrize_data(invalid_groups_file_path, False)

# Объединение всех данных для тестирования групп
test_group_data = valid_groups_data + invalid_groups_data

# Параметризация тестов для validate_group с использованием данных из файлов
@pytest.mark.parametrize("group, expected", test_group_data)
def test_validate_group(group, expected):
    assert validate_group(group) == expected


# Пути к файлам с данными для дат
valid_dates_file_path = os.path.join(os.path.dirname(__file__), './data/valid_dates.txt')
invalid_dates_file_path = os.path.join(os.path.dirname(__file__), './data/invalid_dates.txt')

# Получение данных для дат
valid_dates_data = parametrize_data(valid_dates_file_path, True)
invalid_dates_data = parametrize_data(invalid_dates_file_path, False)

# Объединение всех данных для тестирования дат
test_date_data = valid_dates_data + invalid_dates_data

# Параметризация тестов для validate_date с использованием данных из файлов
@pytest.mark.parametrize("date, expected", test_date_data)
def test_validate_date(date, expected):
    assert validate_date(date) == expected


# Пути к файлам с данными для телефонов
valid_phones_file_path = os.path.join(os.path.dirname(__file__), './data/valid_phones.txt')
invalid_phones_file_path = os.path.join(os.path.dirname(__file__), './data/invalid_phones.txt')

# Получение данных для телефонов
valid_phones_data = parametrize_data(valid_phones_file_path, True)
invalid_phones_data = parametrize_data(invalid_phones_file_path, False)

# Объединение всех данных для тестирования телефонов
test_phone_data = valid_phones_data + invalid_phones_data

# Параметризация тестов для validate_phone с использованием данных из файлов
@pytest.mark.parametrize("phone, expected", test_phone_data)
def test_validate_phone(phone, expected):
    assert validate_phone(phone) == expected
