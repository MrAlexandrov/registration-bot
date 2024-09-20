import json
import os

# Храним состояния пользователей в памяти
user_states = {}

def load_scenario():
    """Загружаем сценарий из JSON файла и возвращаем состояния."""
    scenario_path = os.path.join(os.path.dirname(__file__), '../scenario.json')
    try:
        with open(scenario_path, 'r', encoding='utf-8') as f:
            scenario = json.load(f)
            if "states" not in scenario:
                raise KeyError("Ключ 'states' не найден в сценарии.")
            return scenario["states"]
    except FileNotFoundError:
        print(f"Ошибка: Файл сценария '{scenario_path}' не найден.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Ошибка: Некорректный JSON формат в файле '{scenario_path}': {e}")
        return {}
    except KeyError as e:
        print(f"Ошибка: {e}")
        return {}

def get_user_state(user_id):
    """Получение текущего состояния пользователя."""
    return user_states.get(user_id, "start")

def set_user_state(user_id, state):
    """Установка текущего состояния пользователя."""
    user_states[user_id] = state
