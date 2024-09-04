import os
from fastapi import UploadFile
import subprocess


class Filemanager:
    """
    A helper class to interact with the files in the www_root.
    """

    def __init__(self):
        self.www_root = os.getenv("WWW_ROOT", "/var/www/html")

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
        Deletes a folder in the www_root, centered around the provided path, even if it has files.
        """
        folder_path = os.path.join(self.www_root, path)
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                self.delete_folder(
                    os.path.relpath(os.path.join(root, name), self.www_root)
                )
        os.rmdir(folder_path)

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
                    "7z",
                    "x",
                    "-y",
                    f"{self.www_root}/{path}/{name}",
                    f"-o{self.www_root}/{path}",
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            return e.stderr.decode()

    def composer(self, path: str):
        """
        Runs composer in the provided path.
        """
        try:
            response = subprocess.run(
                ["composer", "install", "--no-dev"],
                cwd=f"{self.www_root}/{path}",
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            return e.stderr.decode()

        return response.stdout.decode()
