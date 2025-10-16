"""
Тесты для валидаторов опроса.
"""

import pytest

from src.survey.validators import (
    DateValidator,
    EmailValidator,
    GroupValidator,
    NonEmptyValidator,
    OptionsValidator,
    PhoneValidator,
    ValidatorFactory,
    YesNoValidator,
    validate_date,
    validate_email,
    validate_group,
    validate_non_empty,
    validate_phone,
    validate_yes_no,
)


class TestNonEmptyValidator:
    """Тесты для NonEmptyValidator."""

    def test_valid_text(self):
        validator = NonEmptyValidator()
        is_valid, error = validator.validate("Hello")
        assert is_valid is True
        assert error is None

    def test_text_with_spaces(self):
        validator = NonEmptyValidator()
        is_valid, error = validator.validate("  Hello  ")
        assert is_valid is True
        assert error is None

    def test_empty_string(self):
        validator = NonEmptyValidator()
        is_valid, error = validator.validate("")
        assert is_valid is False
        assert error == "Поле не может быть пустым."

    def test_only_spaces(self):
        validator = NonEmptyValidator()
        is_valid, error = validator.validate("   ")
        assert is_valid is False
        assert error == "Поле не может быть пустым."

    def test_custom_error_message(self):
        validator = NonEmptyValidator("Кастомная ошибка")
        is_valid, error = validator.validate("")
        assert is_valid is False
        assert error == "Кастомная ошибка"


class TestPhoneValidator:
    """Тесты для PhoneValidator."""

    @pytest.mark.parametrize(
        "phone", ["+79998887766", "89998887766", "79998887766", "8 (999) 888-77-66", "+7 999 888 77 66"]
    )
    def test_valid_phones(self, phone):
        validator = PhoneValidator()
        is_valid, error = validator.validate(phone)
        assert is_valid is True
        assert error is None

    @pytest.mark.parametrize(
        "phone",
        ["9998887766", "abc", "123", "+1234567890", ""],  # без кода страны  # неправильный код страны
    )
    def test_invalid_phones(self, phone):
        validator = PhoneValidator()
        is_valid, error = validator.validate(phone)
        assert is_valid is False
        assert error is not None


class TestEmailValidator:
    """Тесты для EmailValidator."""

    @pytest.mark.parametrize("email", ["test@example.com", "user.name@domain.co.uk", "test123@test-domain.org"])
    def test_valid_emails(self, email):
        validator = EmailValidator()
        is_valid, error = validator.validate(email)
        assert is_valid is True
        assert error is None

    @pytest.mark.parametrize("email", ["test@example", "test", "@example.com", "test@", ""])
    def test_invalid_emails(self, email):
        validator = EmailValidator()
        is_valid, error = validator.validate(email)
        assert is_valid is False
        assert error is not None


class TestDateValidator:
    """Тесты для DateValidator."""

    @pytest.mark.parametrize(
        "date",
        ["01.01.2000", "31.12.1999", "15.06.2008", "1.1.2008", "29.02.2008"],  # високосный год
    )
    def test_valid_dates(self, date):
        validator = DateValidator()
        is_valid, error = validator.validate(date)
        assert is_valid is True
        assert error is None

    @pytest.mark.parametrize("date", ["2000-01-01", "32.12.2022", "01.13.2022", "abc", ""])
    def test_invalid_dates(self, date):
        validator = DateValidator()
        is_valid, error = validator.validate(date)
        assert is_valid is False
        assert error is not None


class TestOptionsValidator:
    """Тесты для OptionsValidator."""

    def test_valid_option(self):
        options = ["Да", "Нет", "Возможно"]
        validator = OptionsValidator(options)
        is_valid, error = validator.validate("Да")
        assert is_valid is True
        assert error is None

    def test_invalid_option(self):
        options = ["Да", "Нет"]
        validator = OptionsValidator(options)
        is_valid, error = validator.validate("Возможно")
        assert is_valid is False
        assert error is not None


class TestYesNoValidator:
    """Тесты для YesNoValidator."""

    @pytest.mark.parametrize("value", ["Да", "Нет"])
    def test_valid_values(self, value):
        validator = YesNoValidator()
        is_valid, error = validator.validate(value)
        assert is_valid is True
        assert error is None

    @pytest.mark.parametrize("value", ["Yes", "No", "Возможно", ""])
    def test_invalid_values(self, value):
        validator = YesNoValidator()
        is_valid, error = validator.validate(value)
        assert is_valid is False
        assert error is not None


class TestGroupValidator:
    """Тесты для GroupValidator."""

    @pytest.mark.parametrize(
        "group",
        [
            "М9-11",  # Basic valid group
            "ИС9-11",  # With faculty code
            "Э9-11",  # Single letter faculty
            "МС9-11",  # Two letter faculty
            "МЦ9-11",  # Different faculty code
            "М91-11",  # With number
            "М91с-11",  # With faculty and number
            "М91с-11а",  # With subgroup
            "М91с-11ав",  # With full subgroup
            "ИУ7-41",  # Real example
            "ФН12-32",  # Another real example
            "Э5-12",  # Simple case
        ],
    )
    def test_valid_groups(self, group):
        validator = GroupValidator()
        is_valid, error = validator.validate(group)
        assert is_valid is True
        assert error is None

    @pytest.mark.parametrize(
        "group",
        [
            "",  # Empty string
            "M9-11",  # Latin instead of Cyrillic
            "М999-11",  # Too many numbers
            "М9-01",  # Invalid class number (0 prefix)
            "М9-100",  # Invalid class number (too many digits)
            "М9-1",  # Missing second digit
            "ММММММ-11",  # Too many letters
            "М9-11аа",  # Invalid subgroup
            "М9-11авв",  # Too long subgroup
        ],
    )
    def test_invalid_groups(self, group):
        validator = GroupValidator()
        is_valid, error = validator.validate(group)
        assert is_valid is False
        assert error is not None


class TestValidatorFactory:
    """Тесты для ValidatorFactory."""

    def test_create_non_empty(self):
        validator = ValidatorFactory.create_non_empty()
        assert isinstance(validator, NonEmptyValidator)

    def test_create_phone(self):
        validator = ValidatorFactory.create_phone()
        assert isinstance(validator, PhoneValidator)

    def test_create_email(self):
        validator = ValidatorFactory.create_email()
        assert isinstance(validator, EmailValidator)

    def test_create_date(self):
        validator = ValidatorFactory.create_date()
        assert isinstance(validator, DateValidator)

    def test_create_group(self):
        validator = ValidatorFactory.create_group()
        assert isinstance(validator, GroupValidator)

    def test_create_options(self):
        options = ["A", "B", "C"]
        validator = ValidatorFactory.create_options(options)
        assert isinstance(validator, OptionsValidator)
        assert validator.options == options

    def test_create_yes_no(self):
        validator = ValidatorFactory.create_yes_no()
        assert isinstance(validator, YesNoValidator)


class TestCompatibilityFunctions:
    """Тесты для функций обратной совместимости."""

    def test_validate_non_empty(self):
        is_valid, error = validate_non_empty("test")
        assert is_valid is True
        assert error is None

    def test_validate_phone(self):
        is_valid, error = validate_phone("+79998887766")
        assert is_valid is True
        assert error is None

    def test_validate_email(self):
        is_valid, error = validate_email("test@example.com")
        assert is_valid is True
        assert error is None

    def test_validate_date(self):
        is_valid, error = validate_date("01.01.2000")
        assert is_valid is True
        assert error is None

    def test_validate_yes_no(self):
        is_valid, error = validate_yes_no("Да")
        assert is_valid is True
        assert error is None

    def test_validate_group(self):
        is_valid, error = validate_group("М9-11")
        assert is_valid is True
        assert error is None

        is_valid, error = validate_group("Invalid")
        assert is_valid is False
        assert error is not None
