import os
import string
import uuid
from os import path

UPLOAD_FOLDER = ""


class FileManager:
    __instance = None

    @staticmethod
    def get_instance() -> 'FileManager':
        """ Static access method. """
        if FileManager.__instance is None:
            FileManager()
        return FileManager.__instance

    def __init__(self):
        self.upload_folder = path.dirname(path.dirname(path.abspath(__file__)))
        self.notebooks_folder = path.join(self.upload_folder, 'notebooks')

        self.__check_folder(self.notebooks_folder)

        if FileManager.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            FileManager.__instance = self

    def __check_folder(self, path):
        if not os.path.isdir(path):
            os.mkdir(path)

    def delete_notebook_file(self, tenant_id: str, code:str):
        tenant_folder = path.join(self.notebooks_folder, tenant_id)

        file_path = tenant_folder + os.path.sep + code + ".ipynb"
        if os.path.isfile(file_path):
            os.remove(file_path)

        o_file_path = tenant_folder + os.path.sep + code + ".ipynb"
        if os.path.isfile(o_file_path):
            os.remove(o_file_path)

    def save_notebook_file(self, tenant_id: str, file):
        tenant_folder = path.join(self.notebooks_folder, tenant_id)
        self.__check_folder(tenant_folder)

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
            'file_path': file_path
        }
