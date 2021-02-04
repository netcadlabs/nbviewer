from nbconvert import HTMLExporter
from boar.running import run_notebook
import nbformat


class NotebookRunner:

    def run(self, notebook_file_path):
        html_exporter = HTMLExporter()
        html_exporter.template_name = 'classic'

        outputs = run_notebook(notebook_file_path, inputs={"a": 1}, verbose=True)

        notebook_content = open(notebook_file_path, 'r').read()
        notebook = nbformat.reads(notebook_content, as_version=4)
        (body, resources) = html_exporter.from_notebook_node(notebook)

        return (body, resources)

    def run_with_cmd(self, notebook_file_path):
        import subprocess
        subprocess.call(['./abc.py', arg1, arg2])
