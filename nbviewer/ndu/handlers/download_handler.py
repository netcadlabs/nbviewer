from nbviewer.nbmanager.database_instance import DatabaseInstance
from nbviewer.nbmanager.filemanager import FileManager
from nbviewer.ndu.handlers.ndu_base_handler import NDUBaseHandler


class DownloadHandler(NDUBaseHandler):
    def get_pattern(self):
        return r"/download/?(.*)"

    def get(self, *path_args, **path_kwargs):
        uri_parts = self.request.uri.split('/')

        if len(uri_parts) != 4:
            self.set_status(400)
            self.finish()
            return

        tenant_id = uri_parts[2]
        notebook_code = uri_parts[3]

        if notebook_code and '.' in notebook_code:
            notebook_code = notebook_code.split('.')[0]

        try:
            notebook = DatabaseInstance.get().get_notebook_by_code(notebook_code)

            file_manager = FileManager.get_instance()
            content = file_manager.notebook_content(tenant_id, notebook_code)

            self.set_header('Content-Type', 'application/octet-stream')
            self.set_header('Content-Disposition', 'attachment; filename=' + notebook['file_name'])
            self.write(content)
            self.finish()
        except FileNotFoundError as fne:
            self.set_status(404)
            self.finish(self.render_template("output_not_found.html", message=str(fne)))
