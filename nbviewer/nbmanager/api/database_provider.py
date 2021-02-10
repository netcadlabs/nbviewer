from abc import ABC, abstractmethod


class DatabaseProvider(ABC):

    @abstractmethod
    def save_notebook(self, nb):
        pass

    @abstractmethod
    def get_tenant_notebooks(self, tenant_id: str):
        pass

    @abstractmethod
    def get_notebook_by_code(self, tenant_id: str, code: str):
        pass

    @abstractmethod
    def update_notebook(self, tenant_id: str, code: str, fields):
        pass

    @abstractmethod
    def delete_notebook(self, tenant_id: str, code: str):
        pass

    def convert_row_map(self, row):
        column_order = ['id', 'tenant_id', 'code', 'name', 'desc', 'file_name', 'path',
                        'c_date', 'exe_date', 'exe_count', 'cron', 'timeout', 'error']
        index = 0
        result = {}
        for column_name in column_order:
            result[column_name] = row[index]
            index = index + 1

        return result
