from pprint import pprint
import httplib2
import googleapiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials

class SpreadsheetError(Exception):
    """Базовое исключение для работы с Google Sheets"""
    pass

class SpreadsheetNotSetError(SpreadsheetError):
    """Исключение для случаев, когда таблица не задана"""
    pass

class SheetNotSetError(SpreadsheetError):
    """Исключение для случаев, когда лист не задан"""
    pass

class GoogleSpreadsheetClient:
    def __init__(self, credentials_file, debug_mode=False):
        self.debug_mode = debug_mode
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(
            credentials_file, 
            ['https://www.googleapis.com/auth/spreadsheets', 
             'https://www.googleapis.com/auth/drive']
        )
        self.http_auth = self.credentials.authorize(httplib2.Http())
        self.sheet_service = googleapiclient.discovery.build('sheets', 'v4', http=self.http_auth)
        self.drive_service = None
        self.spreadsheet_id = None
        self.sheet_id = None
        self.sheet_title = None
        self.requests = []
        self.value_ranges = []

    def share(self, permissions_body):
        """Делится доступом к Google таблице"""
        if not self.spreadsheet_id:
            raise SpreadsheetNotSetError("Таблица не установлена")
        if not self.drive_service:
            self.drive_service = googleapiclient.discovery.build('drive', 'v3', http=self.http_auth)
        share_response = self.drive_service.permissions().create(
            fileId=self.spreadsheet_id,
            body=permissions_body,
            fields='id'
        ).execute()
        if self.debug_mode:
            pprint(share_response)

    def share_read_access(self, email):
        self.share({'type': 'user', 'role': 'reader', 'emailAddress': email})

    def share_write_access(self, email):
        self.share({'type': 'user', 'role': 'writer', 'emailAddress': email})

    def set_spreadsheet(self, spreadsheet_id):
        """Устанавливает активную таблицу по ID"""
        spreadsheet = self.sheet_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        if self.debug_mode:
            pprint(spreadsheet)
        self.spreadsheet_id = spreadsheet['spreadsheetId']
        
        # Изначально не устанавливаем лист — пользователь может выбрать любой
        self.sheet_id = None
        self.sheet_title = None

    def list_sheets(self):
        """Возвращает список всех листов в таблице"""
        if not self.spreadsheet_id:
            raise SpreadsheetNotSetError("Таблица не установлена")
        spreadsheet = self.sheet_service.spreadsheets().get(spreadsheetId=self.spreadsheet_id).execute()
        return [
            {
                "sheetId":  sheet['properties']['sheetId'], 
                "title":    sheet['properties']['title']
            }
            for sheet in spreadsheet['sheets']
        ]

    def set_sheet_by_title(self, sheet_title):
        """Устанавливает активный лист по его названию"""
        sheets = self.list_sheets()
        for sheet in sheets:
            if sheet['title'] == sheet_title:
                self.sheet_id = sheet['sheetId']
                self.sheet_title = sheet['title']
                return
        raise SheetNotSetError(f"Лист с названием '{sheet_title}' не найден")

    def set_sheet_by_id(self, sheet_id):
        """Устанавливает активный лист по его ID"""
        sheets = self.list_sheets()
        for sheet in sheets:
            if sheet['sheetId'] == sheet_id:
                self.sheet_id = sheet['sheetId']
                self.sheet_title = sheet['title']
                return
        raise SheetNotSetError(f"Лист с ID '{sheet_id}' не найден")

    def prepare_set_values(self, start_cell, values, major_dimension="ROWS"):
        """Готовит значения для вставки в таблицу"""
        if not self.sheet_title:
            raise SheetNotSetError("Лист не установлен")
        cells_range = make_range_by_array(start_cell, values)
        self.value_ranges.append({
            "range": f"{self.sheet_title}!{cells_range}",
            "majorDimension": major_dimension,
            "values": values
        })

    def get_values_by_range(self, output_range):
        """Возвращает значения по диапазону"""
        if not self.sheet_title:
            raise SheetNotSetError("Лист не установлен")
        table_range = f"{self.sheet_title}!{output_range}"
        return self.sheet_service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=table_range).execute().get('values', [])

    def get_values(self, rows, cols):
        """Возвращает значения по координатам"""
        return self.get_values_by_range(make_range_from_beginning(rows, cols))

    def execute_batch_update(self, value_input_option="USER_ENTERED"):
        """Запускает пакетный запрос к Google Sheets"""
        if not self.spreadsheet_id:
            raise SpreadsheetNotSetError("Таблица не установлена")
        
        update_responses = {'requests': [], 'values': []}
        try:
            if self.requests:
                update_responses['requests'] = self.sheet_service.spreadsheets().batchUpdate(
                    spreadsheetId=self.spreadsheet_id, 
                    body={"requests": self.requests}
                ).execute()
                if self.debug_mode:
                    pprint(update_responses['requests'])
            
            if self.value_ranges:
                update_responses['values'] = self.sheet_service.spreadsheets().values().batchUpdate(
                    spreadsheetId=self.spreadsheet_id, 
                    body={"valueInputOption": value_input_option, "data": self.value_ranges}
                ).execute()
                if self.debug_mode:
                    pprint(update_responses['values'])
        finally:
            self.requests.clear()
            self.value_ranges.clear()

        return update_responses

def make_range(start_cell, rows, cols):
    """Создает диапазон ячеек"""
    col_letter, row_number = start_cell[0], start_cell[1:]

    assert len(col_letter) == 1 and col_letter.isalpha() and 'A' <= col_letter <= 'Z', "Неверная буква колонки"
    assert 1 <= int(row_number) <= 1000, "Номер строки должен быть в диапазоне [1, 1000]"
    assert ord(col_letter) + cols - 1 <= ord('Z'), "Неверный диапазон по колонкам"

    return f"{start_cell}:{chr(ord(col_letter) + cols - 1)}{int(row_number) + rows - 1}"

def make_range_by_array(start_cell, values):
    """Создает диапазон на основе массива значений"""
    return make_range(start_cell, len(values), len(values[0]))

def make_range_from_beginning(rows, cols):
    """Создает диапазон с начала таблицы"""
    return make_range('A1', rows, cols)