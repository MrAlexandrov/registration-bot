import pytest
import os
from src.validators import validate_group, validate_date, validate_phone


# Универсальная функция для чтения данных из файла
def read_groups_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        groups = [line.strip() for line in file if line.strip()]  # Убираем пустые строки
    return groups

# Универсальный параметризованный тест
def parametrize_groups(file_path, expected_result):
    # Чтение групп из указанного файла
    groups = read_groups_from_file(file_path)
    # Возвращаем список кортежей (группа, ожидаемый результат)
    return [(group, expected_result) for group in groups]

# Пути к файлам с данными
valid_groups_file_path = os.path.join(os.path.dirname(__file__), './data/valid_groups.txt')
invalid_groups_file_path = os.path.join(os.path.dirname(__file__), './data/invalid_groups.txt')

# Получение данных из файлов
valid_groups_data = parametrize_groups(valid_groups_file_path, True)
invalid_groups_data = parametrize_groups(invalid_groups_file_path, False)

# Объединение всех данных для тестирования
test_data = valid_groups_data + invalid_groups_data

# Параметризация тестов с использованием данных из обоих файлов
@pytest.mark.parametrize("group, expected", test_data)
def test_validate_group(group, expected):
    assert validate_group(group) == expected

# Тесты для validate_date
@pytest.mark.parametrize("date, expected", [
    ('31.12.2023', True),
    ('01.01.2000', True),
    ('29.02.2020', True),  # Високосный год
    ('32.01.2023', False),  # День больше 31
    ('31.13.2023', False),  # Месяц больше 12
    ('01.01.99', False),    # Неверный формат года
])
def test_validate_date(date, expected):
    assert validate_date(date) == expected

@pytest.mark.parametrize("phone, expected", [
    ('89001234567', True),
    ('+71234567890', True),
    ('+7-123-456-7890', True),  # Номер с кодом страны
    ('123456', False),         # Меньше 10 цифр
    ('abcdefghij', False),     # Буквы вместо цифр
    ('8900123456789', False),  # Слишком много цифр
    ('89001', False),          # Слишком мало цифр
])
def test_validate_phone(phone, expected):
    assert validate_phone(phone) == expected