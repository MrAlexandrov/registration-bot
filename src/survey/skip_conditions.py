"""
Условия пропуска вопросов для опроса.
Следует принципу Single Responsibility - каждое условие отвечает за одну проверку.
"""
from typing import Dict, Any, Protocol


class SkipCondition(Protocol):
    """Протокол для условий пропуска."""

    def should_skip(self, user_data: Dict[str, Any]) -> bool:
        """Определяет, нужно ли пропустить вопрос."""
        ...


class FieldValueSkipCondition:
    """Условие пропуска на основе значения другого поля."""

    def __init__(self, field_name: str, skip_values: list):
        self.field_name = field_name
        self.skip_values = skip_values if isinstance(skip_values, list) else [skip_values]

    def should_skip(self, user_data: Dict[str, Any]) -> bool:
        field_value = user_data.get(self.field_name)
        return field_value in self.skip_values


class FieldNotValueSkipCondition:
    """Условие пропуска, если поле НЕ равно определенному значению."""

    def __init__(self, field_name: str, required_value: str):
        self.field_name = field_name
        self.required_value = required_value

    def should_skip(self, user_data: Dict[str, Any]) -> bool:
        field_value = user_data.get(self.field_name)
        return field_value != self.required_value


class MultipleFieldsSkipCondition:
    """Условие пропуска на основе нескольких полей (И)."""

    def __init__(self, conditions: list):
        self.conditions = conditions

    def should_skip(self, user_data: Dict[str, Any]) -> bool:
        return all(condition.should_skip(user_data) for condition in self.conditions)


class AnyFieldSkipCondition:
    """Условие пропуска на основе нескольких полей (ИЛИ)."""

    def __init__(self, conditions: list):
        self.conditions = conditions

    def should_skip(self, user_data: Dict[str, Any]) -> bool:
        return any(condition.should_skip(user_data) for condition in self.conditions)


# Фабрика условий пропуска
class SkipConditionFactory:
    """Фабрика для создания условий пропуска."""

    @staticmethod
    def create_field_value(field_name: str, skip_values) -> FieldValueSkipCondition:
        return FieldValueSkipCondition(field_name, skip_values)

    @staticmethod
    def create_field_not_value(field_name: str, required_value: str) -> FieldNotValueSkipCondition:
        return FieldNotValueSkipCondition(field_name, required_value)

    @staticmethod
    def create_multiple_and(conditions: list) -> MultipleFieldsSkipCondition:
        return MultipleFieldsSkipCondition(conditions)

    @staticmethod
    def create_multiple_or(conditions: list) -> AnyFieldSkipCondition:
        return AnyFieldSkipCondition(conditions)


# Предопределенные условия для удобства
def skip_if_other_education(user_data: Dict[str, Any]) -> bool:
    """Пропустить, если выбрано не 'Другое учебное заведение'."""
    condition = SkipConditionFactory.create_field_not_value("education_choice", "Другое учебное заведение")
    return condition.should_skip(user_data)


def skip_if_finished_or_not_studying(user_data: Dict[str, Any]) -> bool:
    """Пропустить, если закончил учебу или не учится."""
    condition = SkipConditionFactory.create_field_value("education_choice", ["Закончил(а)", "Не учусь"])
    return condition.should_skip(user_data)


def skip_if_not_working(user_data: Dict[str, Any]) -> bool:
    """Пропустить, если не работает."""
    condition = SkipConditionFactory.create_field_value("work", "Нет")
    return condition.should_skip(user_data)


def skip_if_no_diploma(user_data: Dict[str, Any]) -> bool:
    """Пропустить, если нет диплома."""
    condition = SkipConditionFactory.create_field_value("diplom", "Нет")
    return condition.should_skip(user_data)


def skip_if_bmstu_student(user_data: Dict[str, Any]) -> bool:
    """Пропустить, если студент МГТУ."""
    condition = SkipConditionFactory.create_field_value("education_choice", "МГТУ им. Баумана")
    return condition.should_skip(user_data)
