import json
import time
import uuid
from datetime import datetime

from nbviewer.nbmanager.database_instance import DatabaseInstance, DATETIME_FORMAT
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.nbmanager.nb_run_error import NotebookRunError
from nbviewer.nbmanager.runner import NotebookRunner
from nbviewer.nbmanager.scheduler_instance import SchedulerInstance
from nbviewer.providers.base import BaseHandler
from bs4 import BeautifulSoup

tenantId = 'test-tenant-id'


def get_argument_value(arguments: dict, name, default_value=''):
    if arguments and arguments.get(name, None) is not None:
        values = arguments.get(name)
        value = None
        if len(values) > 0:
            value = values[0]
            if isinstance(value, bytes):
                value = value.decode("utf-8")

        if value is not None:
            if default_value is not None and isinstance(default_value, int):
                value = int(value)
            return value

    return default_value


def __get_notebook(tenant_id, code):
    notebook = DatabaseInstance.get().get_tenant_notebooks(tenant_id, code)
    return clean_data_for_ui(notebook)


def clean_data_for_ui(item: dict):
    remove_keys = ['path']
    for key in remove_keys:
        if key in item:
            item.pop(key)
    return item


def extract_cron_obj(arguments: dict) -> str:
    result = {
        'interval_type': get_argument_value(arguments, 'interval_type', None),
        'every_type': get_argument_value(arguments, 'every_type', None),
        'every_interval': get_argument_value(arguments, 'every_interval', None),
        'each_type': get_argument_value(arguments, 'each_type', None),
        'each_time': get_argument_value(arguments, 'each_time', None),
    }

    return json.dumps(result)


nb_handler_action_codes = ['run', 'delete']
nb_handler_run_log_action_codes = ['run_logs', 'clear_run_logs']


class NotebookUploadHandler(BaseHandler):
    """Render the upload page"""

    # def __init__(self):
    #     self.database = Database()

    def render_index_template(self, notebooks, **other):
        return self.render_template(
            "notebooks.html",
            title=self.frontpage_setup.get("title", None),
            subtitle=self.frontpage_setup.get("subtitle", None),
            text=self.frontpage_setup.get("text", None),
            show_input=self.frontpage_setup.get("show_input", True),
            notebooks=notebooks,
            **other
        )

    async def __run_command(self, code: str, action: str):
        database = DatabaseInstance.get()
        notebook = database.get_notebook_by_code(code)

        result = {'result': True}

        if code is not None:
            if action == 'run':
                runner = NotebookRunner()
                try:
                    await runner.run_w(notebook)
                    result['data'] = clean_data_for_ui(database.get_notebook_by_code(code))
                except NotebookRunError as nre:
                    result = {'result': False, 'error': nre.args[0]}
            elif action == 'delete':
                self.__delete_notebook(tenantId, code)
        else:
            result = {'result': False, 'error': 'Unknown action'}

        return result

    def __run_logs_command(self, code: str, action: str):
        database = DatabaseInstance.get()
        result = {'result': True}
        if action == 'run_logs':
            notebook = database.get_notebook_by_code(code)
            run_logs = database.get_notebook_run_logs(notebook['id'])
            result = {'data': run_logs}
        elif action == 'clear_run_logs':
            result = {'result': False}

        return result

    async def get(self, *path_args, **path_kwargs):
        code = self.get_argument('code', None)
        action = self.get_argument('action', None)

        if action in nb_handler_action_codes:
            result = await self.__run_command(code, action)
        elif action in nb_handler_run_log_action_codes:
            result = self.__run_logs_command(code, action)
        else:
            result = self.render_index_template(self.__get_notebooks(tenantId))

        self.finish(result)

    def delete(self, code):
        args = self.request.query_arguments
        rendered_template = self.render_index_template(self.__get_notebooks(tenantId))
        self.finish(rendered_template)

    async def post(self, *path_args, **path_kwargs):
        try:
            if self.request.files is not None and self.request.files['file'] is not None \
                    and len(self.request.files['file']) > 0:
                file = self.request.files['file'][0]

                file_manager = FileManager.get_instance()
                database = DatabaseInstance.get()

                name = get_argument_value(self.request.body_arguments, 'name', '')
                desc = get_argument_value(self.request.body_arguments, 'desc', '')
                run = get_argument_value(self.request.body_arguments, 'run', 'off')
                cron_state = get_argument_value(self.request.body_arguments, 'cron_state', 'off')
                cron = ''
                if cron_state == 'on':
                    cron = extract_cron_obj(self.request.body_arguments)
                timeout = get_argument_value(self.request.body_arguments, 'timeout', 0)

                if timeout is not None and timeout > 300:
                    timeout = 60

                result = file_manager.save_notebook_file(tenantId, file)
                if result is not None:
                    notebook = {
                        'tenant_id': tenantId,
                        'code': result['code'],
                        'file_name': result['file_name'],
                        'path': result['path'],
                        'name': str(name),
                        'desc': str(desc),
                        'cron': cron,
                        'timeout': timeout
                    }
                    database.save_notebook(notebook)
                    notebook = DatabaseInstance.get().get_notebook_by_code(notebook['code'])

                    if run == 'on':
                        notebook_runner = NotebookRunner()
                        await notebook_runner.run_w(notebook)

                    SchedulerInstance.get().add_notebook_job(notebook)

        except Exception as e:
            print(e)

        notebooks = self.__get_notebooks(tenantId)
        rendered_template = self.render_index_template(notebooks)
        self.finish(rendered_template)

    def __delete_notebook(self, tenant_id, code):
        database = DatabaseInstance.get()
        database.delete_notebook(tenant_id, code)
        file_manager = FileManager.get_instance()
        file_manager.delete_notebook_file(tenant_id, code)
        return True

    def __get_notebooks(self, tenant_id):
        database = DatabaseInstance.get()
        notebooks = database.get_tenant_notebooks(tenant_id)
        for item in notebooks:
            item = clean_data_for_ui(item)
            item['preview_img'] = item['code'] + ".img"

        return notebooks


NOT_ALLOWED_OUTPUT_SOURCES = ['style.min.css.map', 'custom.css']

HIDDEN_OUTPUT_CLASSES = ['prompt', 'input_prompt', 'output_prompt', 'input']


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


class NotebookHtmlOutputHandler(BaseHandler):

    def get(self, *path_args, **path_kwargs):
        uri_parts = self.request.uri.split('/')

        code = None
        if len(uri_parts) > 2:
            code = uri_parts[2]

        if '?' in code:
            code = code.split('?')[0]

        # if code in NOT_ALLOWED_OUTPUT_SOURCES:
        #     self.finish('')
        #     return

        if not is_valid_uuid(code):
            self.finish('Not valid output code')
            return

        hide_inputs = self.get_argument('hide-inputs', True)

        try:
            file_manager = FileManager.get_instance()
            content = file_manager.notebook_html_content(tenantId, code)

            if hide_inputs:
                soup = BeautifulSoup(content)
                for cls in HIDDEN_OUTPUT_CLASSES:
                    removals = soup.find_all('div', {'class': cls})
                    for match in removals:
                        match.decompose()
                content = str(soup)

            self.finish(content)
        except FileNotFoundError as fne:
            self.set_status(404)
            self.finish(self.render_template("output_not_found.html", message=str(fne)))
