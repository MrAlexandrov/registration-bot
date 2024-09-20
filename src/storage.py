import os
import csv
from spreadsheets import GoogleSpreadsheetClient
from user import User
from settings import FIELDNAMES

class UserStorage:
    """Абстрактный интерфейс для хранения данных пользователей."""
    def save_user(self, user):
        raise NotImplementedError

    def get_all_users(self):
        raise NotImplementedError

class CSVFileStorage(UserStorage):
    """Класс для хранения данных пользователей в CSV-файле."""
    
    def __init__(self, file_name="users.csv", fieldnames=FIELDNAMES):
        """
        :param file_name: Имя CSV-файла.
        :param fieldnames: Список полей (столбцов), которые будут использоваться в файле.
        """
        self.file_name = file_name
        self.fieldnames = fieldnames
        
        # Проверяем, существует ли файл
        if not os.path.exists(self.file_name):
            # Создаем файл, если его нет, и добавляем заголовки
            with open(self.file_name, 'w', newline='', encoding='utf-8') as current_file:
                writer = csv.DictWriter(current_file, fieldnames=self.fieldnames)
                writer.writeheader()

    def save_user(self, user):
        """Сохранение объекта пользователя в CSV-файл."""
        with open(self.file_name, 'a', newline='', encoding='utf-8') as current_file:
            writer = csv.DictWriter(current_file, fieldnames=self.fieldnames)
            writer.writerow(user.to_dict())

    def get_all_users(self):
        """Чтение всех зарегистрированных пользователей из CSV-файла."""
        users = []
        with open(self.file_name, 'r', newline='', encoding='utf-8') as current_file:
            reader = csv.DictReader(current_file)
            for row in reader:
                user = User.from_dict(row)
                users.append(user)
        return users


class GoogleSheetsStorage(UserStorage):
    def __init__(self, credentials_file, spreadsheet_id, fieldnames=FIELDNAMES, sheet_id=0, sheet_title=None, debug_mode=False):
        self.client = GoogleSpreadsheetClient(credentials_file, debug_mode)
        self.client.set_spreadsheet(spreadsheet_id)
        self.fieldnames = fieldnames

        if sheet_title is None:
            self.client.set_sheet_by_id(sheet_id)
        else:
            self.client.set_sheet_by_title(sheet_title)

        # Проверяем, есть ли заголовки на первом ряду
        existing_data = self.client.get_values_by_range('A1:A1')
        if not existing_data:
            # Если заголовков нет, записываем их
            self.client.prepare_set_values('A1', [self.fieldnames])
            self.client.execute_batch_update()

        # Определяем пустую строку, куда можно добавлять данные
        all_data = self.client.get_values_by_range("A1:E")
        self.empty_row = len(all_data) + 1

    def save_user(self, user):
        """Сохранение объекта пользователя в Google таблицу."""
        values = [list(user.to_dict().values())]
        self.client.prepare_set_values('A' + str(self.empty_row), values)
        self.empty_row += 1
        self.client.execute_batch_update()

    def get_all_users(self):
        """Чтение всех зарегистрированных пользователей из Google таблицы."""
        values = self.client.get_values_by_range("A1:E")
        headers = values[0] if values else []
        users = []
        for row in values[1:]:
            if len(row) == len(headers):
                user_data = dict(zip(headers, row))
                users.append(User.from_dict(user_data))
        return users


class CombinedStorage(UserStorage):
    """Класс для хранения данных как в CSV-файле, так и в Google таблице."""
    
    def __init__(self, csv_file_name, credentials_file, spreadsheet_id, fieldnames=FIELDNAMES, sheet_id=0, sheet_title=None, debug_mode=False):
        """
        Инициализация хранилищ данных для CSV и Google таблицы.
        
        :param csv_file_name: Имя файла CSV.
        :param credentials_file: Путь к файлу с учетными данными для Google API.
        :param spreadsheet_id: ID Google таблицы.
        :param fieldnames: Список полей (столбцов).
        :param sheet_id: ID листа Google таблицы.
        :param sheet_title: Название листа Google таблицы.
        :param debug_mode: Флаг включения режима отладки.
        """
        self.csv_storage = CSVFileStorage(file_name=csv_file_name, fieldnames=fieldnames)
        self.google_storage = GoogleSheetsStorage(credentials_file, spreadsheet_id, fieldnames=fieldnames, sheet_id=sheet_id, sheet_title=sheet_title, debug_mode=debug_mode)

    def save_user(self, user):
        """Сохранение данных пользователя в оба хранилища."""
        self.csv_storage.save_user(user)
        self.google_storage.save_user(user)

    def get_all_users(self):
        """Получение всех пользователей из обоих хранилищ."""
        # Читаем из обоих хранилищ (можно вернуть только из одного или объединить данные, если это нужно)
        csv_users = self.csv_storage.get_all_users()
        google_users = self.google_storage.get_all_users()
        
        # Здесь можно выбрать, как поступить с данными из двух источников (например, объединить, проверить дубликаты и т.п.)
        # return {
        #     "csv_users": csv_users,
        #     "google_users": google_users
        # }
        return google_users
