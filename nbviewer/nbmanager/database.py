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
            'tenant_id': row[1],
            'code': row[2],
            'name': row[3],
            'file_name': row[4],
            'path': row[5],
            'c_date': row[6],
            'exe_date': row[7],
            'exe_count': row[8],
            'cron': row[8],
            'timeout': row[9],
            'error': row[10]
        }

    def get_notebooks(self, tenant_id: str):
        result = []
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM notebook where tenant_id = '%s'" % tenant_id)
        for row in res:
            result.append(self.__convert_row_map(row))

        return result

    def save_notebook(self, nb):
        cursor = self.conn.cursor()

        created_date = datetime.now().strftime(DATETIME_FORMAT)
        cursor.execute("INSERT INTO notebook(tenant_id, code, name, file_name, path, c_date, cron) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?)", (nb['tenant_id'], nb['code'], nb['name'], nb['file_name'], nb['path'], created_date, nb['cron']))
        self.conn.commit()

    def update_notebook(self, tenant_id: str, code: str, fields):
        cursor = self.conn.cursor()

        question_marks = ""
        params = []
        for key in fields:
            question_marks = question_marks + (key + ' = ?, ')
            params.append(fields[key])

        if len(question_marks) > 0:
            question_marks = question_marks[:-2]

        params.extend([tenant_id, code])
        cursor.execute("UPDATE notebook SET %s WHERE tenant_id = ? AND code = ?" % question_marks, params)
        self.conn.commit()

    def delete_notebook(self, tenant_id: str, code: str):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notebook WHERE tenant_id = '%s' AND code = '%s'" % (tenant_id, code))
        self.conn.commit()

    def get_notebook(self, tenant_id: str, code: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notebook WHERE tenant_id = '%s' AND code = '%s'" % (tenant_id, code))
        row = cursor.fetchone()
        if row is not None:
            return self.__convert_row_map(row)
        return None

    def run_sql(self, sql) -> sqlite3.Cursor:
        try:
            c = self.conn.cursor()
            return c.execute(sql)
        except sqlite3.Error as e:
            print(e)
