from bs4 import BeautifulSoup

from nbviewer.nbmanager.database_instance import DatabaseInstance
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.ndu.handlers.ndu_base_handler import NDUBaseHandler

HIDDEN_OUTPUT_CLASSES = ['prompt', 'input_prompt', 'output_prompt', 'input']
NOT_ALLOWED_OUTPUT_SOURCES = ['style.min.css.map', 'custom.css']


class NotebookHtmlOutputHandler(NDUBaseHandler):

    def get_pattern(self):
        return r"/outputs/?(.*)"

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

        if not self.is_valid_uuid(code):
            self.finish('Not valid output code')
            return

        database = DatabaseInstance.get()
        notebook = database.get_notebook_by_code(code)

        if not notebook:
            self.finish('Not valid output code 2')
            return

        hide_inputs = self.get_argument('hide-inputs', True)

        try:
            file_manager = FileManager.get_instance()
            content = file_manager.notebook_html_content(notebook['tenant_id'], code)

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
