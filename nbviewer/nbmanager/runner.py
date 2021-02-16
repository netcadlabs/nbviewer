from datetime import datetime
from subprocess import CalledProcessError, STDOUT
import subprocess
from nbconvert import HTMLExporter
import nbformat

from nbviewer.nbmanager.database_instance import DatabaseInstance, DATETIME_FORMAT
from nbviewer.nbmanager.nb_run_error import NotebookRunError

CALL_EXECUTION_TIMEOUT_ERROR_PATTERN = "Cell execution timed out"


# async def run_with_cmd(notebook_file_path, output: str = 'output', format: str = 'html', timeout: int = None):
#

class NotebookRunner:

    def run(self, notebook_file_path):
        html_exporter = HTMLExporter()
        html_exporter.template_name = 'classic'

        # outputs = self.run_notebook(notebook_file_path, inputs={"a": 1}, verbose=True)

        notebook_content = open(notebook_file_path, 'r').read()
        notebook = nbformat.reads(notebook_content, as_version=4)
        (body, resources) = html_exporter.from_notebook_node(notebook)

        return (body, resources)

    async def run_notebook(self, notebook):


        timeout = notebook['timeout']
        output = notebook['code']
        notebook_file_path = notebook['path']
        format = 'html'

        output_name = str(output) + '.' + str(format)
        try:
            result = ''
            command_args = ['jupyter', 'nbconvert', '--execute', notebook_file_path, '--output', output_name]

            if timeout is not None and timeout != 0 and isinstance(timeout, int):
                command_args.append("--ExecutePreprocessor.timeout={}".format(timeout))

            if format == 'html':
                command_args.extend(['--to', 'html'])
                result = subprocess.check_output(command_args, stderr=STDOUT)
            else:
                return False
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
