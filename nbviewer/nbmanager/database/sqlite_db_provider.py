import sqlite3
from datetime import datetime
from os import path
import logging

from nbviewer.nbmanager.api.database_provider import DatabaseProvider

DATETIME_FORMAT = '%d-%m-%Y %H:%M:%S'

nb_columns = ['id', 'tenant_id', 'code', 'name', 'desc', 'file_name', 'path',
              'c_date', 'exe_date', 'exe_count', 'cron', 'timeout', 'error']

rl_columns = ['id', 'tenant_id', 'notebook_id', 'notebook_code', 'code', 'exe_date', 'exe_time', 'error']


class SQLiteDbProvider(DatabaseProvider):

    def __init__(self, config: dict = {}, log: any = None):
        super().__init__(log)
        self.DATABASE_FOLDER = config.get('folder', path.dirname(path.dirname(path.abspath(__file__))))
        self.DB_FILE_NAME = config.get('file', 'notebooks.db')
        self.DB_FILE_PATH = path.join(self.DATABASE_FOLDER, self.DB_FILE_NAME)

        self.log.info('DATABASE_FOLDER = %s' % self.DATABASE_FOLDER)
        self.log.info('DB_FILE_NAME = %s' % self.DB_FILE_NAME)
        self.log.info('DB_FILE_PATH = %s' % self.DB_FILE_PATH)

        self.conn: sqlite3.Connection = None
        self.__create_connection(self.DB_FILE_PATH)

        sql_file = path.join(path.dirname(path.abspath(__file__)), "db.sql")
        sql = None
        with open(sql_file, 'r') as file:
            sql = file.read()

        if sql is not None:
            statements = sql.split(';')
            for query in statements:
                query = str(query).strip('\r\n')
                if query:
                    self.__run_sql(query)

    def __run_sql(self, sql) -> sqlite3.Cursor:
        try:
            c = self.conn.cursor()
            return c.execute(sql)
        except sqlite3.Error as e:
            print(e)
        except sqlite3.Warning as w:
            print(w)

    def __create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            self.conn = sqlite3.connect(db_file, check_same_thread=False)
            print(sqlite3.version)
        except sqlite3.Error as e:
            self.log.error("Failed to initialize sql lite connection : %s", e)
            print(e)

    def save_notebook(self, nb):
        cursor = self.conn.cursor()

        created_date = datetime.now().strftime(DATETIME_FORMAT)
        cursor.execute("INSERT INTO notebook(tenant_id, code, name, desc, file_name, path, c_date, cron, timeout) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                       (nb['tenant_id'], nb['code'], nb['name'], nb['desc'], nb['file_name'],
                        nb['path'], created_date, nb['cron'], nb['timeout']))
        self.conn.commit()

    def get_all_notebooks(self):
        result = []
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM notebook")
        for row in res:
            result.append(self.convert_row_map(row, nb_columns))

        return result

    def get_tenant_notebooks(self, tenant_id: str):
        result = []
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM notebook where tenant_id = ?", [tenant_id])
        for row in res:
            result.append(self.convert_row_map(row, nb_columns))

        return result

    def get_notebook_by_code(self, code: str):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM notebook WHERE code = ?", [code])
        row = cursor.fetchone()
        if row is not None:
            return self.convert_row_map(row, nb_columns)
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

    def delete_notebook(self, tenant_id: str, code: str, delete_run_logs: bool = True):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM notebook WHERE tenant_id = ? AND code = ?", [tenant_id, code])
        self.conn.commit()
        if delete_run_logs:
            cursor.execute("DELETE FROM run_log WHERE notebook_code = ?", [code])
            self.conn.commit()

    def save_run_log(self, rl):
        cursor = self.conn.cursor()
        # created_date = datetime.now().strftime(DATETIME_FORMAT)
        cursor.execute("INSERT INTO run_log(tenant_id, notebook_id, notebook_code, code, exe_date, exe_time, error) "
                       "VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (rl['tenant_id'], rl['notebook_id'], rl['notebook_code'], rl['code'], rl['exe_date'], rl['exe_time'], rl['error']))
        self.conn.commit()

    def get_notebook_run_logs(self, notebook_id: int, limit: int = 15):
        result = []
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM run_log WHERE notebook_id = ?  ORDER BY id DESC LIMIT ?", [notebook_id, limit])
        for row in res:
            result.append(self.convert_row_map(row, rl_columns))

        return result

    def get_notebook_last_run_log(self, notebook_id: int):
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM run_log WHERE notebook_id = ?  ORDER BY id DESC LIMIT ?", [notebook_id, 1])
        for row in res:
            return self.convert_row_map(row, rl_columns)

        return None

    def get_run_log_by_code(self, output_code: int):
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM run_log WHERE code = ?  ORDER BY id DESC LIMIT ?", [output_code, 1])
        for row in res:
            return self.convert_row_map(row, rl_columns)

        return None

    def get_run_log_by_id(self, run_log_id: int):
        cursor = self.conn.cursor()
        res = cursor.execute("SELECT * FROM run_log WHERE id = ?  ORDER BY id DESC LIMIT ?", [run_log_id, 1])
        for row in res:
            return self.convert_row_map(row, rl_columns)

        return None

    def get_run_log_by_ids(self, run_log_ids: list):
        result = []
        cursor = self.conn.cursor()
        res = cursor.execute('SELECT * FROM run_log WHERE id IN ({0})'.format(','.join(['?' for c in run_log_ids])), run_log_ids)
        for row in res:
            result.append(self.convert_row_map(row, rl_columns))

        return result

    def delete_run_logs_by_notebook_code(self, notebook_code):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM run_log WHERE notebook_code = ?", [notebook_code])
        self.conn.commit()
