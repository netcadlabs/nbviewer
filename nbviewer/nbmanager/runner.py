import os
import time
import uuid
from datetime import datetime
from subprocess import CalledProcessError, STDOUT
import subprocess
from nbconvert import HTMLExporter
import nbformat

from nbviewer.nbmanager.database_instance import DatabaseInstance, DATETIME_FORMAT
from nbviewer.nbmanager.nb_run_error import NotebookRunError

CALL_EXECUTION_TIMEOUT_ERROR_PATTERN = "Cell execution timed out"


class NotebookRunner:

    def run(self, notebook_file_path):
        html_exporter = HTMLExporter()
        html_exporter.template_name = 'classic'

        # outputs = self.run_notebook(notebook_file_path, inputs={"a": 1}, verbose=True)

        notebook_content = open(notebook_file_path, 'r').read()
        notebook = nbformat.reads(notebook_content, as_version=4)
        (body, resources) = html_exporter.from_notebook_node(notebook)

        return (body, resources)

    async def run_no_db(self, notebook):
        try:
            await self.__run_notebook(notebook)
        except NotebookRunError as nre:
            error = nre.args[0]
            print(nre)
        except Exception as e:
            error = 'Unknown error while running notebook!'

    async def run_w(self, notebook):
        code = notebook['code']
        tenant_id = notebook['tenant_id']

        output_code = str(uuid.uuid4())

        database = DatabaseInstance.get()
        error = None
        exe_date = datetime.now().strftime(DATETIME_FORMAT)
        start_time = time.time()
        try:
            await self.__run_notebook(notebook, output_code=output_code)
        except NotebookRunError as nre:
            error = nre.args[0]
            print(nre)
        except Exception as e:
            error = 'Unknown error while running notebook!'

        run_log = {
            'tenant_id': tenant_id,
            'notebook_id': notebook['id'],
            'notebook_code': code,
            'code': output_code,
            'exe_date': exe_date,
            'exe_time': time.time() - start_time,
            'error': None
        }

        if error:
            database.update_notebook(tenant_id, code, {'error': error, 'exe_date': exe_date})
            run_log['error'] = error
        else:
            # file_manager = FileManager.get_instance()
            # file_manager.create_preview_of_notebook(tenantId, code)
            database.update_notebook(tenant_id, code, {'error': None, 'exe_date': exe_date})

        database.save_run_log(run_log)

    async def __run_notebook(self, notebook, output_code: str = None):
        timeout = notebook['timeout']
        notebook_code = notebook['code']
        notebook_file_path = notebook['path']
        output_format = 'html'

        output_name = str(notebook_code) + '.' + str(output_format)
        if output_code:
            output_name = os.path.join('outputs', str(output_code) + '.' + str(output_format))

        try:
            result = ''
            command_args = ['jupyter', 'nbconvert', '--execute', notebook_file_path, '--output', output_name]

            if timeout is not None and timeout != 0 and isinstance(timeout, int):
                command_args.append("--ExecutePreprocessor.timeout={}".format(timeout))

            if output_format == 'html':
                command_args.extend(['--to', 'html'])
                result = subprocess.check_output(command_args, stderr=STDOUT)
            else:
                return
        except CalledProcessError as err:
            if err.output:
                error_detail = str(err.output.decode('UTF-8'))
                if CALL_EXECUTION_TIMEOUT_ERROR_PATTERN in error_detail:
                    error_detail = CALL_EXECUTION_TIMEOUT_ERROR_PATTERN
                raise NotebookRunError(error_detail)
            else:
                raise NotebookRunError('Can not run notebook!')

        return True

    @staticmethod
    def run_notebook_thread(self, notebook):
        pass
