import os
import mimetypes
import urllib
from fastapi import UploadFile


class Filemanager:
    """
    A helper class to interact with all of the nginx config files, given set paths.
    """

    def __init__(self, www_root: str):
        self.www_root = www_root
        self.mime = mimetypes.MimeTypes()

    def list_files(self, path: str = ""):
        """
        List all files in the sites-available directory, and the first 6 lines of each file, and whether it is enabled.
        """
        files = os.listdir(self.www_root + path)

        return [
            {
                "name": name,
                "filesize": os.stat(f"{self.www_root}{path}/{name}").st_size,
                "is_dir": os.path.isdir(f"{self.www_root}{path}/{name}"),
            }
            for name in files
        ]

    def get_file(self, name: str):
        """
        Get the contents of a file in the sites-available directory.
        """
        try:
            with open(f"{self.www_root}/{name}", "r") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete_file(self, name: str):
        """
        Delete a file in the sites-available directory.
        """
        os.remove(f"{self.www_root}/{name}")

    def delete_folder(self, name: str):
        """
        Delete a folder in the sites-available directory.
        """
        os.rmdir(f"{self.www_root}/{name}")

    def create_file(self, path: str, content: UploadFile):
        """
        Create a file in the sites-available directory.
        """
        with open(f"{self.www_root}/{path}/{content.filename}", "wb") as f:
            f.write(content.file.read())

    def create_folder(self, path: str):
        """
        Create a folder in the sites-available directory.
        """
        os.mkdir(f"{self.www_root}/{path}")
