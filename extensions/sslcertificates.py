import os
from OpenSSL import crypto


class SSLCertificates:
    """
    This extension provides a way to manage SSL certificates.
    """

    def __init__(self):
        self.ssl_root = os.getenv("SSL_ROOT", "/var/www/certificates")

    def list_certificates(self):
        """
        List all certificates in the provided path, centered around the ssl_root.
        """
        return [
            certificate
            for certificate in [
                self.get_certificate(certificate)
                for certificate in os.listdir(self.ssl_root)
            ]
            if certificate is not None
        ]

    def get_certificate(self, site: str):
        """
        Return the important data about a certificate
        """
        try:
            with open(f"{self.ssl_root}/{site}/fullchain.pem", "r") as f:
                fullchain = f.read()
            try:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, fullchain)
            except crypto.Error:
                return None
            return {
                "site": site,
                "valid_sites": [
                    cert[4:] for cert in cert.get_extension(6).__str__().split(", ")
                ],
                "issuer": cert.get_issuer().O,
                "not_before": cert.get_notBefore(),
                "not_after": cert.get_notAfter(),
                "has_expired": cert.has_expired(),
                "fullchain": fullchain,
            }
        except FileNotFoundError:
            return None

    def replace_certificate(self, site: str, fullchain: str, privkey: str):
        """
        Replaces a certificate in the ssl_root, centered around the provided site.
        """
        with open(f"{self.ssl_root}/{site}/fullchain.pem", "w") as f:
            f.write(fullchain)
        with open(f"{self.ssl_root}/{site}/privkey.pem", "w") as f:
            f.write(privkey)

    def delete_certificate(self, site: str):
        """
        Deletes a certificate in the ssl_root, centered around the provided site.
        """
        os.remove(f"{self.ssl_root}/{site}/fullchain.pem")
        os.remove(f"{self.ssl_root}/{site}/privkey.pem")
        os.rmdir(f"{self.ssl_root}/{site}")

    def create_certificate(self, site: str, fullchain: str, privkey: str):
        """
        Creates a certificate in the provided site.
        """
        os.makedirs(f"{self.ssl_root}/{site}")
        with open(f"{self.ssl_root}/{site}/fullchain.pem", "w") as f:
            f.write(fullchain)
        with open(f"{self.ssl_root}/{site}/privkey.pem", "w") as f:
            f.write(privkey)
