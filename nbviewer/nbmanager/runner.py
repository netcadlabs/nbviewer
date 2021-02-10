from datetime import datetime
from subprocess import CalledProcessError, STDOUT

from nbconvert import HTMLExporter
import nbformat

from nbviewer.nbmanager.database_instance import DatabaseInstance, DATETIME_FORMAT
from nbviewer.nbmanager.nb_run_error import NotebookRunError


def run_with_cmd(notebook_file_path, output: str = 'output', format: str = 'html'):
    import subprocess

    output_name = str(output) + '.' + str(format)
    try:
        result = ''
        if format == 'html':
            result = subprocess.check_output(['jupyter', 'nbconvert', '--to', 'html', '--execute', notebook_file_path, '--output', output_name],
                                             stderr=STDOUT)
        else:
            return False
    except CalledProcessError as err:
        if err.output:
            raise NotebookRunError(err.output.decode('UTF-8'))
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

        if run_with_cmd(notebook['path'], notebook['code'], 'html'):
            exe_date = datetime.now().strftime(DATETIME_FORMAT)
            DatabaseInstance.get().update_notebook(tenant_id, code, {'exe_date': exe_date})
            return True

        return False

    @staticmethod
    def run_notebook_thread(self, notebook):
        pass
