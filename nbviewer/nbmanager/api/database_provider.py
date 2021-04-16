from abc import ABC, abstractmethod


class DatabaseProvider(ABC):

    def __init__(self, log):
        self.log = log

    @abstractmethod
    def save_notebook(self, nb):
        pass

    @abstractmethod
    def get_all_notebooks(self):
        pass

    @abstractmethod
    def get_tenant_notebooks(self, tenant_id: str):
        pass

    @abstractmethod
    def get_notebook_by_code(self, code: str):
        pass

    @abstractmethod
    def update_notebook(self, tenant_id: str, code: str, fields):
        pass

    @abstractmethod
    def delete_notebook(self, tenant_id: str, code: str):
        pass

    @abstractmethod
    def save_run_log(self, nb):
        pass

    @abstractmethod
    def get_notebook_run_logs(self, notebook_id: int):
        pass

    @abstractmethod
    def get_notebook_last_run_log(self, notebook_id: int):
        pass

    @abstractmethod
    def get_run_log_by_code(self, run_log_code: str):
        pass

    @abstractmethod
    def get_run_log_by_id(self, run_log_id: int):
        pass

    @abstractmethod
    def get_run_log_by_ids(self, run_log_ids: list):
        pass

    @abstractmethod
    def delete_run_logs_by_notebook_code(self, notebook_code):
        pass

    def convert_row_map(self, row, column_order):
        index = 0
        result = {}
        for column_name in column_order:
            result[column_name] = row[index]
            index = index + 1

        return result
