from nbviewer.nbmanager.api.database_provider import DatabaseProvider
from nbviewer.nbmanager.database.sqlite_db_provider import SQLiteDbProvider

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
    def get() -> 'DatabaseProvider':
        if DatabaseInstance.__instance is None:
            if DB_TYPE is 'sqlite':
                DatabaseInstance.__instance = SQLiteDbProvider()
            else:
                raise ValueError('%s is not known database provider type'.format(DB_TYPE))
        return DatabaseInstance.__instance
