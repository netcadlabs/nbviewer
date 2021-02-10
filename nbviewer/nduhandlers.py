from nbviewer.nbmanager.database_instance import DatabaseInstance
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.nbmanager.nb_run_error import NotebookRunError
from nbviewer.nbmanager.runner import NotebookRunner
from nbviewer.providers.base import BaseHandler
from bs4 import BeautifulSoup

tenantId = 'test-tenant-id'


def get_argument_value(arguments: dict, name, default_value=''):
    if arguments and arguments.get(name, None) is not None:
        values = arguments.get(name)
        if len(values) > 0:
            value = values[0]
            if isinstance(value, bytes):
                return value.decode("utf-8")
            else:
                return value

    return default_value


def __get_notebook(tenant_id, code):
    notebook = DatabaseInstance.get().get_tenant_notebooks(tenant_id, code)
    return clean_data_for_ui(notebook)


def clean_data_for_ui(item: dict):
    remove_keys = ['path', 'cron']
    for key in remove_keys:
        if key in item:
            item.pop(key)
    return item


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

    def get(self, *path_args, **path_kwargs):
        code = self.get_argument('code', None)
        action = self.get_argument('action', None)
        database = DatabaseInstance.get()

        if code is not None:
            result = {}
            if action == 'run':
                runner = NotebookRunner()
                error = None
                try:
                    runner.run_notebook(tenantId, code)
                except NotebookRunError as nre:
                    error = nre.args[0]
                    print(nre)
                except Exception as e:
                    error = 'Unknown error while running notebook!'

                if error:
                    result = {'result': False, 'error': error}
                    database.update_notebook(tenantId, code, {'error': error})
                else:
                    # file_manager = FileManager.get_instance()
                    # file_manager.create_preview_of_notebook(tenantId, code)
                    result = database.get_notebook_by_code(tenantId, code)
            elif action == 'delete':
                self.__delete_notebook(tenantId, code)
                result = {'result': True}

            self.finish(result)
            return

        rendered_template = self.render_index_template(self.__get_notebooks(tenantId))
        self.finish(rendered_template)

    def delete(self, code):
        args = self.request.query_arguments
        rendered_template = self.render_index_template(self.__get_notebooks(tenantId))
        self.finish(rendered_template)

    def post(self, *path_args, **path_kwargs):
        try:
            if self.request.files is not None and self.request.files['file'] is not None \
                    and len(self.request.files['file']) > 0:
                file = self.request.files['file'][0]

                file_manager = FileManager.get_instance()
                database = DatabaseInstance.get()

                name = get_argument_value(self.request.body_arguments, 'name', '')
                desc = get_argument_value(self.request.body_arguments, 'desc', '')
                run = get_argument_value(self.request.body_arguments, 'run', 0)
                cron = get_argument_value(self.request.body_arguments, 'cron', '')
                timeout = get_argument_value(self.request.body_arguments, 'timeout', 5000)
                if timeout is not None and timeout < 100:
                    timeout = 100

                result = file_manager.save_notebook_file(tenantId, file)
                if result is not None:
                    notebook = {
                        'tenant_id': tenantId,
                        'code': result['code'],
                        'file_name': result['file_name'],
                        'path': result['path'],
                        'name': str(name),
                        'desc': str(desc),
                        'cron': str(cron),
                        'timeout': timeout
                    }
                    database.save_notebook(notebook)

                if str(run) == str('1'):
                    runner = NotebookRunner.run_notebook_thread()

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

        return False

        # try:
        #     (body, resources) = runner.run(notebook['path'])
        #
        #     output_name = code + ".html"
        #     f = open(output_name, "a")
        #     f.write(body)
        #     f.close()
        # except Exception as e:
        #     print(e)

    def __get_notebooks(self, tenant_id):
        database = DatabaseInstance.get()
        notebooks = database.get_tenant_notebooks(tenant_id)
        for item in notebooks:
            item = clean_data_for_ui(item)
            item['preview_img'] = item['code'] + ".img"

        return notebooks


NOT_ALLOWED_OUTPUT_SOURCES = ['style.min.css.map', 'custom.css']

HIDDEN_OUTPUT_CLASSES = ['prompt', 'input_prompt', 'output_prompt', 'input']


class NotebookHtmlOutputHandler(BaseHandler):

    def get(self, *path_args, **path_kwargs):
        code = self.request.uri.split('/').pop()
        if '?' in code:
            code = code.split('?')[0]

        if code in NOT_ALLOWED_OUTPUT_SOURCES:
            self.finish('')
            return

        hide_inputs = self.get_argument('hide-inputs', False)

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
