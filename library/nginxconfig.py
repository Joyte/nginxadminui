import os


class NginxConfig:
    """
    A helper class to interact with all of the nginx config files, given set paths.
    """

    def __init__(self, sites_available: str, sites_enabled: str):
        self.sites_available = sites_available
        self.sites_enabled = sites_enabled

    def list_files(self):
        """
        List all files in the sites-available directory, and the first 6 lines of each file, and whether it is enabled.
        """
        files = os.listdir(self.sites_available)
        return [
            {
                "filename": filename,
                "content": "\n".join(self.get_file(filename).split("\n")[:6]),
                "enabled": self.check_site_enabled(filename),
            }
            for filename in files
        ]

    def get_file(self, filename: str):
        """
        Get the contents of a file in the sites-available directory.
        """
        with open(f"{self.sites_available}/{filename}", "r") as f:
            return f.read()

    def edit_file(self, filename: str, content: str):
        """
        Edit the contents of a file in the sites-available directory.
        """
        with open(f"{self.sites_available}/{filename}", "w") as f:
            f.write(content)

    def enable_site(self, filename: str):
        """
        Enable a site by creating a symlink in the sites-enabled directory.
        """
        os.symlink(
            f"{self.sites_available}/{filename}", f"{self.sites_enabled}/{filename}"
        )

    def disable_site(self, filename: str):
        """
        Disable a site by removing the symlink in the sites-enabled directory.
        """
        os.remove(f"{self.sites_enabled}/{filename}")

    def check_site_enabled(self, filename: str):
        """
        Check if a site is enabled by checking for the symlink in the sites-enabled directory.
        """
        return os.path.islink(f"{self.sites_enabled}/{filename}")

    def delete_site(self, filename: str):
        """
        Delete a site by removing the file from the sites-available directory.
        """
        if self.check_site_enabled(filename):
            self.disable_site(filename)
        os.remove(f"{self.sites_available}/{filename}")

    def create_site(self, filename: str, content: str):
        """
        Create a new site by writing the content to a file in the sites-available directory.
        """
        with open(f"{self.sites_available}/{filename}", "w") as f:
            f.write(content)
