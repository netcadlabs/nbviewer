from nbviewer.nbmanager.database_instance import DatabaseInstance
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.nbmanager.nb_run_error import NotebookRunError
from nbviewer.nbmanager.runner import NotebookRunner
from nbviewer.nbmanager.scheduler_instance import SchedulerInstance
from nbviewer.ndu.handlers.ndu_base_handler import NDUBaseHandler
from nbviewer.ndu.utils import clean_data_for_ui, get_argument_value, extract_cron_obj

nb_handler_action_codes = ['run', 'delete']
nb_handler_run_log_action_codes = ['run_logs', 'clear_run_logs']


class NotebookUpdateHandler(NDUBaseHandler):
    """ """

    def get_pattern(self):
        return r"/notebook-update/?(.*)"

    async def post(self, *path_args, **path_kwargs):
        try:
            curr_user = self.check_token()
            tenant_id = curr_user['tenantId']

            self.log.info("Start notebook updating...")
            if self.request.files is not None and self.request.files['file'] is not None \
                    and len(self.request.files['file']) > 0:
                file = self.request.files['file'][0]

                file_manager = FileManager.get_instance()

                code = get_argument_value(self.request.body_arguments, 'code', '')
                notebook = DatabaseInstance.get().get_notebook_by_code(code)

                if notebook is None:
                    raise ValueError('notebook with this code not found')

                file_manager.update_notebook_file(tenant_id, code, file)

                # if result is not None:
                #     self.log.info("Notebook file saved")
                #     database.save_notebook(notebook)
                # else:
                #     self.log.info("Can not save notebook file...")

        except Exception as e:
            self.log.warn("Notebook upload error =%s", e)
            print(e)

        self.redirect('/notebooks')
