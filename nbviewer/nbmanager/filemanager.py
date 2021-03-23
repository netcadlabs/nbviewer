import os
import pwd
import shutil
import uuid
from os import path

try:  # Python 3.8
    from functools import cached_property
except ImportError:
    from nbviewer.utils import cached_property


# import imgkit
def get_username():
    return pwd.getpwuid(os.getuid())[0]


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
            self.__log_debug('data folder going to created : {}'.format(NB_DATA_FOLDER), is_info=True)
            NB_DATA_FOLDER = DEFAULT_FOLDER
            check_folder(NB_DATA_FOLDER)

        return NB_DATA_FOLDER

    def __log_error(self, message: str):
        if self.log:
            self.log.error(message)

    def __log_debug(self, message: str, is_info: bool = False):
        if self.log:
            if is_info:
                self.log.info(message)
            else:
                self.log.debug(message)

    def __init__(self, log):
        self.log = log
        data_folder = self.get_data_folder
        self.notebooks_folder = path.join(data_folder, 'notebooks')

        if FileManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            FileManager.__instance = self

        self.__log_debug('Current user {}'.format(get_username()), is_info=True)

        if not os.path.isdir(self.notebooks_folder):
            self.__log_debug('Creating notebooks folder : {}'.format(self.notebooks_folder), is_info=True)
            check_folder(self.notebooks_folder)

    def __create_notebook_folder(self, tenant_id, notebook_code):
        tenant_folder = path.join(self.notebooks_folder, tenant_id)

        if not os.path.isdir(tenant_folder):
            self.__log_debug('Creating tenant folder : {}'.format(tenant_folder), is_info=True)
            check_folder(tenant_folder)

        tenant_notebooks_folder = path.join(tenant_folder, notebook_code)
        if not os.path.isdir(tenant_notebooks_folder):
            self.__log_debug('Creating tenant notebook folder : {}'.format(tenant_notebooks_folder), is_info=True)
            check_folder(tenant_notebooks_folder)

        outputs_folder = path.join(tenant_notebooks_folder, 'outputs')
        if not os.path.isdir(outputs_folder):
            self.__log_debug('Creating tenant notebook output folder : {}'.format(outputs_folder), is_info=True)
            check_folder(outputs_folder)

        return tenant_notebooks_folder

    def delete_notebook_file(self, tenant_id: str, code: str):
        notebook_folder = path.join(self.notebooks_folder, tenant_id, code)

        file_path = notebook_folder + os.path.sep + code + ".ipynb"
        if os.path.isfile(file_path):
            os.remove(file_path)

        o_file_path = notebook_folder + os.path.sep + ".outputs"
        if os.path.isdir(o_file_path):
            os.rmdir(o_file_path)

        if os.path.isdir(notebook_folder):
            shutil.rmtree(notebook_folder)

    def save_notebook_file(self, tenant_id: str, file):
        notebook_code = str(uuid.uuid4())

        tenant_folder = self.__create_notebook_folder(tenant_id, notebook_code)

        original_file_name = file['filename']
        extension = os.path.splitext(original_file_name)[1]
        if extension != ".ipynb":
            raise Exception("File extension is not .ipynb")

        final_filename = notebook_code + extension

        file_path = tenant_folder + os.path.sep + final_filename
        with open(file_path, 'wb') as output_file:
            output_file.write(file['body'])

        self.__log_debug('notebook file saved!', is_info=True)
        return {
            'result': True,
            'code': notebook_code,
            'file_name': original_file_name,
            'path': file_path
        }

    def get_notebook_html_content(self, tenant_id, notebook_code, output_code):
        file_path = self.get_notebook_html_file_path(tenant_id, notebook_code, output_code)

        content = None
        if os.path.isfile(file_path):
            with open(file_path) as f:
                content = f.read()
        else:
            raise FileNotFoundError('Output file not found!')

        return content

    def notebook_content(self, tenant_id, code):
        notebook_folder = path.join(self.notebooks_folder, tenant_id, code)
        file_path = notebook_folder + os.path.sep + code + '.ipynb'

        content = None
        if os.path.isfile(file_path):
            with open(file_path) as f:
                content = f.read()
        else:
            raise FileNotFoundError('Notebook file not found!')

        return content

    def get_notebook_html_file_path(self, tenant_id, notebook_code, output_code):
        notebook_folder = path.join(self.notebooks_folder, tenant_id, notebook_code, 'outputs')
        file_path = notebook_folder + os.path.sep + output_code + '.html'

        return file_path

    def create_preview_of_notebook(self, tenant_id, code, source_ext="html", target_ext="jpg"):
        notebook_folder = path.join(self.notebooks_folder, tenant_id, code)
        file_path = notebook_folder + os.path.sep + code + '.' + source_ext
        img_file_path = notebook_folder + os.path.sep + code + '.' + target_ext

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
