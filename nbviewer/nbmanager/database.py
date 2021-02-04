import sqlite3
from datetime import datetime
from os import path

DATABASE_FOLDER = ""
DB_FILE_NAME = "notebooks.db"
DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'


class Database:
    __instance = None

    @staticmethod
    def get_instance() -> 'Database':
        """ Static access method. """
        if Database.__instance is None:
            Database()
        return Database.__instance

    def __init__(self, folder: str = None):
        DATABASE_FOLDER = path.dirname(path.dirname(path.abspath(__file__)))
        self.conn: sqlite3.Connection = None
        self.__create_connection(path.join(DATABASE_FOLDER, DB_FILE_NAME))

        sql_file = path.join(path.dirname(path.dirname(path.abspath(__file__))), "db.sql")
        sql = None
        with open(sql_file, 'r') as file:
            sql = file.read()

        if sql is not None:
            self.run_sql(sql)

        if Database.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Database.__instance = self

    def __get_tenant_files(self):

        pass

    def __create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(db_file)
            print(sqlite3.version)
        except sqlite3.Error as e:
            print(e)

    @staticmethod
    def __convert_row_map(row):
        return {
            'id': row[0],
            'code': row[2],
            'name': row[3],
            'path': row[4],
            'c_date': row[5],
            'exe_date': row[6],
            'exe_count': row[7]
        }

    def get_notebooks(self, tenant_id: str):
        result = []
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM notebook where tenant_id = '%s'" % tenant_id)
        for row in res:
            result.append(self.__convert_row_map(row))

        return result

    def save_notebook(self, tenant_id: str, code: str, name: str, path: str):
        cursor = self.conn.cursor()

        created_date = datetime.now().strftime(DATETIME_FORMAT)
        cursor.execute("INSERT INTO notebook(tenant_id, code, name, path, c_date) VALUES ('%s','%s','%s','%s','%s')"
                       % (tenant_id, code, name, path, created_date))
        self.conn.commit()

    def update_notebook(self, tenant_id: str, code: str, fields):
        cursor = self.conn.cursor()

        set_query = ""
        for key in fields:
            set_query = (key + " = " + fields[key] + ", ")

        if len(set_query) > 0:
            set_query = set_query[:-1]

        cursor.execute("UPDATE notebook %s tenant_id = '%s' AND code = '%s'" % (set_query, tenant_id, code))
        self.conn.commit()

    def delete_notebook(self, tenant_id: str, code: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notebook WHERE tenant_id = '%s' AND code = '%s'" % (tenant_id, code))
        self.conn.commit()

    def get_notebook(self, tenant_id: str, code: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notebook where tenant_id = '%s' AND code = '%s'" % (tenant_id, code))
        row = cursor.fetchone();
        if row is not None:
            return self.__convert_row_map(row)
        return None

    def run_sql(self, sql) -> sqlite3.Cursor:
        try:
            c = self.conn.cursor()
            return c.execute(sql)
        except sqlite3.Error as e:
            print(e)
