"""
Тесты для условий пропуска вопросов.
"""
import pytest
from src.survey.skip_conditions import (
    FieldValueSkipCondition,
    FieldNotValueSkipCondition,
    MultipleFieldsSkipCondition,
    AnyFieldSkipCondition,
    SkipConditionFactory,
    skip_if_other_education,
    skip_if_finished_or_not_studying,
    skip_if_not_working,
    skip_if_no_diploma,
    skip_if_bmstu_student
)


class TestFieldValueSkipCondition:
    """Тесты для FieldValueSkipCondition."""

    def test_should_skip_single_value(self):
        """Тест пропуска по одному значению."""
        condition = FieldValueSkipCondition("work", "Нет")

        # Должен пропустить
        user_data = {"work": "Нет"}
        assert condition.should_skip(user_data) is True

        # Не должен пропустить
        user_data = {"work": "Да"}
        assert condition.should_skip(user_data) is False

        # Поле отсутствует
        user_data = {}
        assert condition.should_skip(user_data) is False

    def test_should_skip_multiple_values(self):
        """Тест пропуска по нескольким значениям."""
        condition = FieldValueSkipCondition("education_choice", ["Закончил(а)", "Не учусь"])

        # Должен пропустить для первого значения
        user_data = {"education_choice": "Закончил(а)"}
        assert condition.should_skip(user_data) is True

        # Должен пропустить для второго значения
        user_data = {"education_choice": "Не учусь"}
        assert condition.should_skip(user_data) is True

        # Не должен пропустить
        user_data = {"education_choice": "МГТУ им. Баумана"}
        assert condition.should_skip(user_data) is False


class TestFieldNotValueSkipCondition:
    """Тесты для FieldNotValueSkipCondition."""

    def test_should_skip_not_value(self):
        """Тест пропуска если поле НЕ равно значению."""
        condition = FieldNotValueSkipCondition("education_choice", "Другое учебное заведение")

        # Должен пропустить (не равно требуемому значению)
        user_data = {"education_choice": "МГТУ им. Баумана"}
        assert condition.should_skip(user_data) is True

        # Не должен пропустить (равно требуемому значению)
        user_data = {"education_choice": "Другое учебное заведение"}
        assert condition.should_skip(user_data) is False

        # Поле отсутствует - должен пропустить
        user_data = {}
        assert condition.should_skip(user_data) is True


class TestMultipleFieldsSkipCondition:
    """Тесты для MultipleFieldsSkipCondition (И)."""

    def test_should_skip_all_conditions_true(self):
        """Тест пропуска когда все условия выполнены."""
        condition1 = FieldValueSkipCondition("work", "Нет")
        condition2 = FieldValueSkipCondition("diplom", "Нет")

        multiple_condition = MultipleFieldsSkipCondition([condition1, condition2])

        # Все условия выполнены - должен пропустить
        user_data = {"work": "Нет", "diplom": "Нет"}
        assert multiple_condition.should_skip(user_data) is True

        # Одно условие не выполнено - не должен пропустить
        user_data = {"work": "Да", "diplom": "Нет"}
        assert multiple_condition.should_skip(user_data) is False


class TestAnyFieldSkipCondition:
    """Тесты для AnyFieldSkipCondition (ИЛИ)."""

    def test_should_skip_any_condition_true(self):
        """Тест пропуска когда любое условие выполнено."""
        condition1 = FieldValueSkipCondition("work", "Нет")
        condition2 = FieldValueSkipCondition("diplom", "Нет")

        any_condition = AnyFieldSkipCondition([condition1, condition2])

        # Одно условие выполнено - должен пропустить
        user_data = {"work": "Нет", "diplom": "Да"}
        assert any_condition.should_skip(user_data) is True

        # Другое условие выполнено - должен пропустить
        user_data = {"work": "Да", "diplom": "Нет"}
        assert any_condition.should_skip(user_data) is True

        # Ни одно условие не выполнено - не должен пропустить
        user_data = {"work": "Да", "diplom": "Да"}
        assert any_condition.should_skip(user_data) is False


class TestSkipConditionFactory:
    """Тесты для SkipConditionFactory."""

    def test_create_field_value(self):
        """Тест создания FieldValueSkipCondition."""
        condition = SkipConditionFactory.create_field_value("work", "Нет")
        assert isinstance(condition, FieldValueSkipCondition)
        assert condition.field_name == "work"
        assert condition.skip_values == ["Нет"]

    def test_create_field_not_value(self):
        """Тест создания FieldNotValueSkipCondition."""
        condition = SkipConditionFactory.create_field_not_value("education_choice", "Другое учебное заведение")
        assert isinstance(condition, FieldNotValueSkipCondition)
        assert condition.field_name == "education_choice"
        assert condition.required_value == "Другое учебное заведение"

    def test_create_multiple_and(self):
        """Тест создания MultipleFieldsSkipCondition."""
        condition1 = SkipConditionFactory.create_field_value("work", "Нет")
        condition2 = SkipConditionFactory.create_field_value("diplom", "Нет")

        multiple_condition = SkipConditionFactory.create_multiple_and([condition1, condition2])
        assert isinstance(multiple_condition, MultipleFieldsSkipCondition)
        assert len(multiple_condition.conditions) == 2

    def test_create_multiple_or(self):
        """Тест создания AnyFieldSkipCondition."""
        condition1 = SkipConditionFactory.create_field_value("work", "Нет")
        condition2 = SkipConditionFactory.create_field_value("diplom", "Нет")

        any_condition = SkipConditionFactory.create_multiple_or([condition1, condition2])
        assert isinstance(any_condition, AnyFieldSkipCondition)
        assert len(any_condition.conditions) == 2


class TestPredefinedConditions:
    """Тесты для предопределенных условий."""

    def test_skip_if_other_education(self):
        """Тест пропуска если не 'Другое учебное заведение'."""
        # Должен пропустить
        user_data = {"education_choice": "МГТУ им. Баумана"}
        assert skip_if_other_education(user_data) is True

        # Не должен пропустить
        user_data = {"education_choice": "Другое учебное заведение"}
        assert skip_if_other_education(user_data) is False

    def test_skip_if_finished_or_not_studying(self):
        """Тест пропуска если закончил или не учится."""
        # Должен пропустить - закончил
        user_data = {"education_choice": "Закончил(а)"}
        assert skip_if_finished_or_not_studying(user_data) is True

        # Должен пропустить - не учится
        user_data = {"education_choice": "Не учусь"}
        assert skip_if_finished_or_not_studying(user_data) is True

        # Не должен пропустить
        user_data = {"education_choice": "МГТУ им. Баумана"}
        assert skip_if_finished_or_not_studying(user_data) is False

    def test_skip_if_not_working(self):
        """Тест пропуска если не работает."""
        # Должен пропустить
        user_data = {"work": "Нет"}
        assert skip_if_not_working(user_data) is True

        # Не должен пропустить
        user_data = {"work": "Да"}
        assert skip_if_not_working(user_data) is False

    def test_skip_if_no_diploma(self):
        """Тест пропуска если нет диплома."""
        # Должен пропустить
        user_data = {"diplom": "Нет"}
        assert skip_if_no_diploma(user_data) is True

        # Не должен пропустить
        user_data = {"diplom": "Да"}
        assert skip_if_no_diploma(user_data) is False

    def test_skip_if_bmstu_student(self):
        """Тест пропуска если студент МГТУ."""
        # Должен пропустить
        user_data = {"education_choice": "МГТУ им. Баумана"}
        assert skip_if_bmstu_student(user_data) is True

        # Не должен пропустить
        user_data = {"education_choice": "Другое учебное заведение"}
        assert skip_if_bmstu_student(user_data) is False
