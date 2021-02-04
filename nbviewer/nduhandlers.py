from nbviewer.nbmanager.database import Database
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.nbmanager.runner import NotebookRunner
from nbviewer.providers.base import BaseHandler

tenantId = 'test-tenant-id'


class NotebookUploadHandler(BaseHandler):
    """Render the upload page"""

    # def __init__(self):
    #     self.database = Database()

    def render_index_template(self, notebooks, **other):
        return self.render_template(
            "upload.html",
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
        if code is not None:
            if action == 'run':
                self.__run_notebook(tenantId, code)
            elif action == 'delete':
                self.__delete_notebook(tenantId, code)
            self.finish("OK?")
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
                database = Database.get_instance()

                result = file_manager.save_notebook_file(tenantId, file)
                if result is not None:
                    database.save_notebook(tenantId, result['code'], result['file_name'], result['file_path'])
        except Exception as e:
            print(e)

        notebooks = self.__get_notebooks(tenantId)
        rendered_template = self.render_index_template(notebooks)
        self.finish(rendered_template)

    def __delete_notebook(self, tenant_id, code):
        database = Database.get_instance()
        database.delete_notebook(tenant_id, code)
        file_manager = FileManager.get_instance()
        file_manager.delete_notebook_file(tenant_id, code)

    def __run_notebook(self, tenant_id, code):
        database = Database.get_instance()
        notebook = database.get_notebook(tenant_id, code)
        print(notebook)
        runner = NotebookRunner()

        try:
            (body, resources) = runner.run(notebook['path'])

            output_name = code + ".html"
            f = open(output_name, "a")
            f.write(body)
            f.close()
        except Exception as e:
            print(e)

    @staticmethod
    def __get_notebooks(tenant_id):
        database = Database.get_instance()
        notebooks = database.get_notebooks(tenant_id)
        for item in notebooks:
            item['preview_img'] = item['path'] + ".img"

        return notebooks
