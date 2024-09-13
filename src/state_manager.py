import json

# Храним состояния пользователей в памяти
user_states = {}

def load_scenario():
    """Загружаем сценарий из JSON файла."""
    with open('scenario.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_user_state(user_id):
    """Получение текущего состояния пользователя."""
    return user_states.get(user_id, "start")

def set_user_state(user_id, state):
    """Установка текущего состояния пользователя."""
    user_states[user_id] = state
