from nbviewer.nbmanager.api.database_provider import DatabaseProvider
from nbviewer.nbmanager.database.sqlite_db_provider import SQLiteDbProvider
from nbviewer.nbmanager.filemanager import FileManager

try:  # Python 3.8
    from functools import cached_property
except ImportError:
    from nbviewer.utils import cached_property

DB_TYPE = 'sqlite'
DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'


class DatabaseInstance:
    __instance = None

    # @cached_property
    # def instance(self) -> 'DatabaseProvider':
    #     return DatabaseInstance.__instance

    @staticmethod
    def get(log: any = None) -> 'DatabaseProvider':
        if DatabaseInstance.__instance is None:
            file_manager = FileManager.get_instance(log)
            if DB_TYPE == 'sqlite':
                DatabaseInstance.__instance = SQLiteDbProvider({'folder': file_manager.get_data_folder}, log=log)
            else:
                raise ValueError('%s is not known database provider type'.format(DB_TYPE))
        return DatabaseInstance.__instance
