import os

class UserStorage:
    """Абстрактный интерфейс для хранения данных пользователей."""
    def save_user(self, user_id, user_data):
        raise NotImplementedError

class FileStorage(UserStorage):
    """Класс для хранения данных пользователей в текстовом файле."""
    
    def __init__(self, file_name="users.txt"):
        self.file_name = file_name
        if not os.path.exists(self.file_name):
            with open(self.file_name, 'w') as f:
                f.write("ID пользователя | Имя | Фамилия | Группа | Ник\n")

    def save_user(self, user_id, user_data):
        """Сохранение данных пользователя в текстовый файл."""
        with open(self.file_name, 'a') as f:
            f.write(f"{user_id} | {user_data['first_name']} | {user_data['last_name']} | {user_data['group']} | {user_data['username']}\n")

    def get_all_users(self):
        """Чтение всех зарегистрированных пользователей из файла."""
        users = []
        with open(self.file_name, 'r') as f:
            next(f)  # Пропускаем заголовок
            for line in f:
                parts = line.strip().split(" | ")
                if len(parts) == 5:
                    user_id = int(parts[0])
                    first_name = parts[1]
                    users.append((user_id, first_name))
        return users
