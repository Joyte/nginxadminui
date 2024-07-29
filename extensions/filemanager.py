import os
import mimetypes
import urllib
from fastapi import UploadFile
import subprocess


class Filemanager:
    """
    A helper class to interact with the files in the provided www_root
    """

    def __init__(self, www_root: str):
        self.www_root = www_root
        self.mime = mimetypes.MimeTypes()

    def list_files(self, path: str = ""):
        """
        List all files in the provided path, centered around the www_root.
        """
        files = os.listdir(self.www_root + "/" + path)

        return [
            {
                "name": name,
                "filesize": os.stat(f"{self.www_root}/{path}/{name}").st_size,
                "is_dir": os.path.isdir(f"{self.www_root}/{path}/{name}"),
            }
            for name in files
        ]

    def get_file(self, path: str):
        """
        Get the content of a file in the www_root.
        """
        try:
            with open(f"{self.www_root}/{path}", "r") as f:
                return f.read()
        except FileNotFoundError:
            return None

    def delete_file(self, path: str, name: str):
        """
        Deletes a file in the www_root, centered around the provided path.
        """
        os.remove(f"{self.www_root}/{path}/{name}")

    def delete_folder(self, path: str):
        """
        Deletes a folder in the www_root, centered around the provided path.
        """
        os.rmdir(f"{self.www_root}/{path}")

    def create_file(self, path: str, content: UploadFile):
        """
        Creates a file in the provided path.
        """
        with open(f"{self.www_root}/{path}/{content.filename}", "wb") as f:
            f.write(content.file.read())

    def create_folder(self, path: str):
        """
        Creates a folder in the provided path.
        """
        os.mkdir(f"{self.www_root}/{path}")

    def unzip_file(self, path: str, name: str):
        """
        Unzips a file in the provided path.

        Returns the error message if there is one.
        """
        try:
            subprocess.run(
                [
                    "unzip",
                    f"{self.www_root}/{path}/{name}",
                    "-d",
                    f"{self.www_root}/{path}",
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            return e.stderr.decode()
