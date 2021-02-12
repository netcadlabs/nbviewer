from datetime import datetime
from subprocess import CalledProcessError, STDOUT

from nbconvert import HTMLExporter
import nbformat

from nbviewer.nbmanager.database_instance import DatabaseInstance, DATETIME_FORMAT
from nbviewer.nbmanager.nb_run_error import NotebookRunError

CALL_EXECUTION_TIMEOUT_ERROR_PATTERN = "Cell execution timed out"


def run_with_cmd(notebook_file_path, output: str = 'output', format: str = 'html', timeout: int = None):
    import subprocess

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


class NotebookRunner:

    def run(self, notebook_file_path):
        html_exporter = HTMLExporter()
        html_exporter.template_name = 'classic'

        # outputs = self.run_notebook(notebook_file_path, inputs={"a": 1}, verbose=True)

        notebook_content = open(notebook_file_path, 'r').read()
        notebook = nbformat.reads(notebook_content, as_version=4)
        (body, resources) = html_exporter.from_notebook_node(notebook)

        return (body, resources)

    def run_notebook(self, tenant_id, code):
        notebook = DatabaseInstance.get().get_notebook_by_code(tenant_id, code)

        if run_with_cmd(notebook['path'], output=notebook['code'], format='html', timeout=notebook['timeout']):
            return True

        return False

    @staticmethod
    def run_notebook_thread(self, notebook):
        pass
