import os
import uuid
from os import path

try:  # Python 3.8
    from functools import cached_property
except ImportError:
    from nbviewer.utils import cached_property


# import imgkit

def check_folder(folder: str):
    try:
        if not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
        return True
    except Exception as e:
        print(e)
        return False

DEFAULT_FOLDER = '/var/nbviewer/data'

class FileManager:
    __instance = None

    @staticmethod
    def get_instance(log: any = None) -> 'FileManager':
        """ Static access method. """
        if FileManager.__instance is None:
            FileManager(log)
        return FileManager.__instance

    @cached_property
    def get_data_folder(self):
        NB_DATA_FOLDER = os.getenv('NB_DATA_FOLDER', DEFAULT_FOLDER)
        if not check_folder(NB_DATA_FOLDER):
            NB_DATA_FOLDER = DEFAULT_FOLDER
            check_folder(NB_DATA_FOLDER)

        return NB_DATA_FOLDER

    def __init__(self, log):
        self.log = log
        data_folder = self.get_data_folder
        self.notebooks_folder = path.join(data_folder, 'notebooks')

        if FileManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            FileManager.__instance = self

    def delete_notebook_file(self, tenant_id: str, code: str):
        tenant_folder = path.join(self.notebooks_folder, tenant_id)

        file_path = tenant_folder + os.path.sep + code + ".ipynb"
        if os.path.isfile(file_path):
            os.remove(file_path)

        o_file_path = tenant_folder + os.path.sep + code + ".html"
        if os.path.isfile(o_file_path):
            os.remove(o_file_path)

    def save_notebook_file(self, tenant_id: str, file):
        tenant_folder = path.join(self.notebooks_folder, tenant_id)
        check_folder(tenant_folder)

        original_file_name = file['filename']
        extension = os.path.splitext(original_file_name)[1]
        if extension != ".ipynb":
            raise Exception("File extension is not .ipynb")
        code = str(uuid.uuid4())
        final_filename = code + extension

        file_path = tenant_folder + os.path.sep + final_filename
        output_file = open(file_path, 'wb')
        output_file.write(file['body'])

        return {
            'result': True,
            'code': code,
            'file_name': original_file_name,
            'path': file_path
        }

    def notebook_html_content(self, tenant_id, code):
        file_path = self.notebook_html_file_path(tenant_id, code)

        content = None
        if os.path.isfile(file_path):
            with open(file_path) as f:
                content = f.read()
        else:
            raise FileNotFoundError('Output file not found!')

        return content

    def notebook_html_file_path(self, tenant_id, code):
        tenant_folder = path.join(self.notebooks_folder, tenant_id)
        file_path = tenant_folder + os.path.sep + code + '.html'

        return file_path

    def create_preview_of_notebook(self, tenant_id, code, source_ext="html", target_ext="jpg"):
        tenant_folder = path.join(self.notebooks_folder, tenant_id)
        file_path = tenant_folder + os.path.sep + code + '.' + source_ext
        img_file_path = tenant_folder + os.path.sep + code + '.' + target_ext

        try:
            if os.path.isfile(file_path):
                # from preview_generator.manager import PreviewManager
                # cache_path = '/tmp/preview_cache'
                # manager = PreviewManager(cache_path, create_folder=True)
                # path_to_preview_image = manager.get_jpeg_preview(file_path, page=1)
                #
                # return path_to_preview_image

                lines = None
                with open(file_path) as f:
                    lines = f.read()

                # if lines is not None:
                #     imgkit.from_string(lines, img_file_path)
        except:
            print('cant create preview')

        return None
