from nbviewer.nbmanager.database_instance import DatabaseInstance
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.nbmanager.nb_run_error import NotebookRunError
from nbviewer.nbmanager.runner import NotebookRunner
from nbviewer.nbmanager.scheduler_instance import SchedulerInstance
from nbviewer.ndu.handlers.ndu_base_handler import NDUBaseHandler
from nbviewer.ndu.utils import clean_data_for_ui, get_argument_value, extract_cron_obj

nb_handler_action_codes = ['run', 'delete']
nb_handler_run_log_action_codes = ['run_logs', 'clear_run_logs']


class NotebooksHandler(NDUBaseHandler):
    """Render the upload page"""

    def get_pattern(self):
        return r"/notebooks/?(.*)"

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
            is_authenticated=self.is_authenticated(),
            **other
        )

    async def __run_command(self, tenant_id: str, code: str, action: str):
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
                self.__delete_notebook(tenant_id, code)
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
        curr_user = self.check_token()
        tenant_id = curr_user['tenantId']

        code = self.get_argument('code', None)
        action = self.get_argument('action', None)

        if action in nb_handler_action_codes:
            result = await self.__run_command(tenant_id, code, action)
        elif action in nb_handler_run_log_action_codes:
            result = self.__run_logs_command(code, action)
        else:
            result = self.render_index_template(self.__get_notebooks(tenant_id))

        self.finish(result)

    def delete(self, code):
        curr_user = self.check_token()
        args = self.request.query_arguments
        rendered_template = self.render_index_template(self.__get_notebooks(curr_user['tenantId']))
        self.finish(rendered_template)

    async def post(self, *path_args, **path_kwargs):
        try:
            curr_user = self.check_token()
            tenant_id = curr_user['tenantId']

            self.log.info("Start notebook upload...")
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

                result = file_manager.save_notebook_file(tenant_id, file)
                if result is not None:
                    self.log.info("Notebook file saved")
                    notebook = {
                        'tenant_id': tenant_id,
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
                        self.log.info("Running uploaded notebook file...")
                        notebook_runner = NotebookRunner()
                        await notebook_runner.run_w(notebook)

                    SchedulerInstance.get().add_notebook_job(notebook)
                else:
                    self.log.info("Can not save notebook file...")

        except Exception as e:
            self.log.warn("Notebook upload error =%s", e)
            print(e)

        notebooks = self.__get_notebooks(tenant_id)
        rendered_template = self.render_index_template(notebooks)
        self.finish(rendered_template)

    def __delete_notebook(self, tenant_id, code):
        SchedulerInstance.get().remove_notebook_job(code)
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
