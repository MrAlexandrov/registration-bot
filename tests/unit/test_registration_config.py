"""
Тесты для системы конфигурации регистрации.
"""
import pytest
from src.registration_config import (
    RegistrationSurveyConfig,
    SurveyField,
    registration_survey,
    POSITIONS,
    AGES,
    PROBABILITIES,
    EDUCATION_OPTIONS,
    YES_NO
)
from src.survey.validators import validate_non_empty, validate_phone
from src.survey.formatters import format_text_db, format_default_display


class TestSurveyField:
    """Тесты для SurveyField."""

    def test_survey_field_creation(self):
        """Тест создания поля опроса."""
        field = SurveyField(
            field_name="test_field",
            label="Тестовое поле",
            message="Введите тестовые данные",
            validator=validate_non_empty,
            db_formatter=format_text_db,
            display_formatter=format_default_display,
            editable=True
        )

        assert field.field_name == "test_field"
        assert field.label == "Тестовое поле"
        assert field.message == "Введите тестовые данные"
        assert field.validator == validate_non_empty
        assert field.db_formatter == format_text_db
        assert field.display_formatter == format_default_display
        assert field.editable is True
        assert field.db_type == "TEXT"

    def test_survey_field_with_options(self):
        """Тест создания поля с вариантами ответов."""
        options = ["Вариант1", "Вариант2", "Вариант3"]
        field = SurveyField(
            field_name="choice_field",
            label="Поле выбора",
            message="Выберите вариант",
            options=options,
            multi_select=True,
            editable=True
        )

        assert field.options == options
        assert field.multi_select is True


class TestRegistrationSurveyConfig:
    """Тесты для RegistrationSurveyConfig."""

    def test_config_initialization(self):
        """Тест инициализации конфигурации."""
        config = RegistrationSurveyConfig()

        assert len(config.fields) > 0
        assert len(config.post_registration_states) > 0
        assert len(config.admin_states) > 0

    def test_get_field_by_name(self):
        """Тест получения поля по имени."""
        config = RegistrationSurveyConfig()

        # Существующее поле
        name_field = config.get_field_by_name("name")
        assert name_field is not None
        assert name_field.field_name == "name"
        assert name_field.label == "Имя"

        # Несуществующее поле
        nonexistent_field = config.get_field_by_name("nonexistent")
        assert nonexistent_field is None

    def test_get_field_by_label(self):
        """Тест получения поля по метке."""
        config = RegistrationSurveyConfig()

        # Существующее поле
        name_field = config.get_field_by_label("Имя")
        assert name_field is not None
        assert name_field.field_name == "name"
        assert name_field.label == "Имя"

        # Несуществующее поле
        nonexistent_field = config.get_field_by_label("Несуществующее поле")
        assert nonexistent_field is None

    def test_get_editable_fields(self):
        """Тест получения редактируемых полей."""
        config = RegistrationSurveyConfig()
        editable_fields = config.get_editable_fields()

        assert len(editable_fields) > 0
        for field in editable_fields:
            assert field.editable is True

    def test_get_field_names(self):
        """Тест получения имен полей."""
        config = RegistrationSurveyConfig()
        field_names = config.get_field_names()

        assert len(field_names) > 0
        assert "name" in field_names
        assert "email" in field_names
        assert "phone" in field_names

    def test_add_field(self):
        """Тест добавления нового поля."""
        config = RegistrationSurveyConfig()
        initial_count = len(config.fields)

        new_field = SurveyField(
            field_name="test_field",
            label="Тестовое поле",
            message="Тестовое сообщение",
            editable=True
        )

        config.add_field(new_field)

        assert len(config.fields) == initial_count + 1
        assert config.get_field_by_name("test_field") is not None

    def test_remove_field(self):
        """Тест удаления поля."""
        config = RegistrationSurveyConfig()

        # Добавляем поле для удаления
        test_field = SurveyField(
            field_name="temp_field",
            label="Временное поле",
            message="Временное сообщение",
            editable=True
        )
        config.add_field(test_field)

        initial_count = len(config.fields)

        # Удаляем поле
        removed = config.remove_field("temp_field")

        assert removed is True
        assert len(config.fields) == initial_count - 1
        assert config.get_field_by_name("temp_field") is None

        # Попытка удалить несуществующее поле
        removed = config.remove_field("nonexistent")
        assert removed is False


class TestGlobalConfig:
    """Тесты для глобального экземпляра конфигурации."""

    def test_registration_survey_exists(self):
        """Тест существования глобального экземпляра."""
        assert registration_survey is not None
        assert isinstance(registration_survey, RegistrationSurveyConfig)

    def test_required_fields_exist(self):
        """Тест наличия обязательных полей."""
        required_fields = ["name", "birth_date", "phone", "email"]

        for field_name in required_fields:
            field = registration_survey.get_field_by_name(field_name)
            assert field is not None, f"Required field '{field_name}' not found"

    def test_field_names_unique(self):
        """Тест уникальности имен полей."""
        field_names = registration_survey.get_field_names()
        assert len(field_names) == len(set(field_names)), "Field names are not unique"

    def test_field_labels_unique(self):
        """Тест уникальности меток полей."""
        field_labels = [field.label for field in registration_survey.fields]
        assert len(field_labels) == len(set(field_labels)), "Field labels are not unique"


class TestConstants:
    """Тесты для констант."""

    def test_positions_not_empty(self):
        """Тест что список должностей не пустой."""
        assert len(POSITIONS) > 0
        assert "Вожатый" in POSITIONS

    def test_ages_not_empty(self):
        """Тест что список возрастов не пустой."""
        assert len(AGES) > 0
        assert "6-9" in AGES

    def test_probabilities_not_empty(self):
        """Тест что список вероятностей не пустой."""
        assert len(PROBABILITIES) > 0
        assert "0-25" in PROBABILITIES

    def test_education_options_not_empty(self):
        """Тест что список образования не пустой."""
        assert len(EDUCATION_OPTIONS) > 0
        assert "МГТУ им. Баумана" in EDUCATION_OPTIONS

    def test_yes_no_options(self):
        """Тест опций Да/Нет."""
        assert len(YES_NO) == 2
        assert "Да" in YES_NO
        assert "Нет" in YES_NO
