from bs4 import BeautifulSoup

from nbviewer.nbmanager.database_instance import DatabaseInstance
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.nbmanager.nb_run_error import NotebookNotFoundError, NotebookOutputError, NotebookOutputNotFoundError
from nbviewer.ndu.handlers.ndu_base_handler import NDUBaseHandler

HIDDEN_OUTPUT_CLASSES = ['prompt', 'input_prompt', 'output_prompt', 'input']
NOT_ALLOWED_OUTPUT_SOURCES = ['style.min.css.map', 'custom.css']


class NotebookHtmlOutputHandler(NDUBaseHandler):

    def get_pattern(self):
        return r"/outputs/?(.*)"

    def get(self, *path_args, **path_kwargs):
        hide_inputs = self.get_argument('hide-inputs', 'True')

        if hide_inputs and hide_inputs.lower() == 'true':
            hide_inputs = True
        else:
            hide_inputs = False

        action = self.get_argument('action', 'show_latest')

        try:
            if action == 'show_latest':
                notebook_code = self.get_argument('nb_code', None)
                self.render_latest_output(notebook_code, hide_inputs=hide_inputs)
            elif action == 'show':
                output_code = self.get_argument('code', None)
                self.render_output(output_code, hide_inputs=hide_inputs)
            elif action == 'compare':
                output_ids = self.get_argument('output_ids', None)
                self.render_compare_outputs(output_ids)
            else:
                self.finish('Not valid action')
        except Exception as fne:
            self.set_status(404)
            self.finish(self.render_template("output_not_found.html", message=str(fne)))

    def render_latest_output(self, notebook_code, hide_inputs=True):
        database = DatabaseInstance.get()
        notebook = database.get_notebook_by_code(notebook_code)

        if notebook is None:
            raise NotebookNotFoundError('Not valid notebook code')

        run_log = database.get_notebook_last_run_log(notebook['id'])

        if run_log is None:
            raise NotebookOutputNotFoundError('Notebook output not found')

        tenant_id = run_log['tenant_id']
        notebook_code = run_log['notebook_code']

        self.render_output(run_log['code'], notebook_code=notebook_code, tenant_id=tenant_id, hide_inputs=hide_inputs)

    def render_output(self, output_code, notebook_code=None, tenant_id=None, hide_inputs=True):
        if not self.is_valid_uuid(output_code):
            raise NotebookOutputError('Not valid output code')

        if tenant_id is None or notebook_code is None:
            database = DatabaseInstance.get()
            run_log = database.get_run_log_by_code(output_code)
            if run_log is None:
                raise NotebookOutputNotFoundError('Notebook output not found')
            tenant_id = run_log['tenant_id']
            notebook_code = run_log['notebook_code']

        content = self.get_output_content(tenant_id, notebook_code, output_code, hide_inputs)
        self.finish(content)

    def render_compare_outputs(self, output_ids):
        ids = output_ids.split(',')
        if len(ids) < 2:
            raise ValueError('output_ids parameter should contain at least 2 value')

        database = DatabaseInstance.get()
        run_logs = database.get_run_log_by_ids(ids)

        containers = []
        content = ''
        compare_div = '<div class="compare-notebooks" id="notebooks">'

        for run_log in run_logs:
            content = self.get_output_content(run_log['tenant_id'], run_log['notebook_code'], run_log['code'], hide_inputs=True)
            soup = BeautifulSoup(content)
            notebook_div = soup.find('div', id="notebook-container")
            # containers.append(notebook_div)

            # compare_div = compare_div + '<div class="compare-single" id="notebooks">'
            # compare_div = compare_div + str(self.__get_output_detail_html(run_log))
            compare_div = compare_div + str(notebook_div)
            # compare_div = compare_div + '</div>'

        compare_div = compare_div + '</div>'

        run_log = run_logs[0]
        content = self.get_output_content(run_log['tenant_id'], run_log['notebook_code'], run_log['code'], hide_inputs=True)
        soup = BeautifulSoup(content)
        notebook_div = soup.find('div', id="notebook")

        notebook_div.clear()
        part = BeautifulSoup(compare_div, 'html.parser')
        notebook_div.append(part)

        head = soup.head
        head.append(soup.new_tag('style', type='text/css'))
        head.style.append('.compare-notebooks {display: flex;}')
        head.style.append('#notebook-container {margin: 4px;border-radius: 10px;}')

        self.finish(str(soup))

    def get_output_content(self, tenant_id, notebook_code, output_code, hide_inputs=True):
        file_manager = FileManager.get_instance()
        content = file_manager.get_notebook_html_content(tenant_id, notebook_code, output_code)

        if hide_inputs:
            soup = BeautifulSoup(content)
            for cls in HIDDEN_OUTPUT_CLASSES:
                removals = soup.find_all('div', {'class': cls})
                for match in removals:
                    match.decompose()
            content = str(soup)

        return content

    def __get_output_detail_html(self, run_log):
        detail_html = "<div style='color:red;'>{} - {} </div>".format(run_log['id'], run_log['code'])
        detail_tag = BeautifulSoup(detail_html, 'html.parser')
        return detail_tag