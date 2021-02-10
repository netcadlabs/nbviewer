import sqlite3
from datetime import datetime
from os import path

from nbviewer.nbmanager.api.database_provider import DatabaseProvider

DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'


class SQLiteDbProvider(DatabaseProvider):
    def __init__(self, config: dict = {}):

        self.DATABASE_FOLDER = config.get('folder', path.dirname(path.dirname(path.abspath(__file__))))
        self.DB_FILE_NAME = config.get('file', 'notebooks.db')

        self.conn: sqlite3.Connection = None
        self.__create_connection(path.join(self.DATABASE_FOLDER, self.DB_FILE_NAME))

        sql_file = path.join(path.dirname(path.abspath(__file__)), "db.sql")
        sql = None
        with open(sql_file, 'r') as file:
            sql = file.read()

        if sql is not None:
            self.__run_sql(sql)

    def __run_sql(self, sql) -> sqlite3.Cursor:
        try:
            c = self.conn.cursor()
            return c.execute(sql)
        except sqlite3.Error as e:
            print(e)

    def __create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(db_file)
            print(sqlite3.version)
        except sqlite3.Error as e:
            print(e)

    def save_notebook(self, nb):
        cursor = self.conn.cursor()

        created_date = datetime.now().strftime(DATETIME_FORMAT)
        cursor.execute("INSERT INTO notebook(tenant_id, code, name, desc, file_name, path, c_date, cron, timeout) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (nb['tenant_id'], nb['code'], nb['name'], nb['desc'], nb['file_name'],
                        nb['path'], created_date, nb['cron'], nb['timeout']))
        self.conn.commit()

    def get_tenant_notebooks(self, tenant_id: str):
        result = []
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM notebook where tenant_id = '%s'" % tenant_id)
        for row in res:
            result.append(self.convert_row_map(row))

        return result

    def get_notebook_by_code(self, tenant_id: str, code: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notebook WHERE tenant_id = '%s' AND code = '%s'" % (tenant_id, code))
        row = cursor.fetchone()
        if row is not None:
            return self.convert_row_map(row)
        return None

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
