import os
from OpenSSL import crypto, SSL
import random
import string


class SSLCertificates:
    """
    This extension provides a way to manage SSL certificates.
    """

    def __init__(self):
        self.ssl_root = os.getenv("SSL_ROOT", "/etc/nginxadminui/certificates")

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

    def get_certificate(self, identifier: str):
        """
        Return the important data about a certificate
        """
        try:
            with open(f"{self.ssl_root}/{identifier}/fullchain.pem", "r") as f:
                fullchain = f.read()
            try:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, fullchain)
            except crypto.Error:
                return None

            cn = ""
            for i in range(cert.get_extension_count()):
                if cert.get_extension(i).get_short_name() == b"subjectAltName":
                    cn = [
                        cert.split(":")[1]
                        for cert in cert.get_extension(i).__str__().split(",")
                    ]
                    break
            if not cn:
                cn = [cert.get_subject().CN]
            return {
                "identifier": identifier,
                "valid_sites": cn,
                "issuer": cert.get_issuer().O,
                "not_before": cert.get_notBefore(),
                "not_after": cert.get_notAfter(),
                "has_expired": cert.has_expired(),
                "fullchain": fullchain,
            }
        except FileNotFoundError:
            return None

    def generate_certificate(self, domain):
        """
        Generates a certificate in the ssl_root, centered around the provided domains.
        """
        key = crypto.PKey()
        key.generate_key(crypto.TYPE_RSA, 4096)

        cert = crypto.X509()
        cert.get_subject().commonName = domain
        cert.get_subject().organizationName = "Nginx Admin UI"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(473040000)  # 15 years in seconds
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(key)
        cert.sign(key, "sha512")

        identifier = "".join(
            random.choices(string.ascii_lowercase + string.digits, k=8)
        )

        self.create_certificate(
            identifier,
            crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"),
            crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"),
        )

        return identifier

    def delete_certificate(self, identifier: str):
        """
        Deletes a certificate in the ssl_root, centered around the provided identifier.
        """
        os.remove(f"{self.ssl_root}/{identifier}/fullchain.pem")
        os.remove(f"{self.ssl_root}/{identifier}/privkey.pem")
        os.rmdir(f"{self.ssl_root}/{identifier}")

    def create_certificate(self, identifier: str, fullchain: str, privkey: str):
        """
        Creates a certificate in the provided identifier.
        """

        # Check if fullchain is valid
        try:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, fullchain)
        except crypto.Error:
            return "Invalid fullchain provided."

        # Check if privkey is valid
        try:
            key = crypto.load_privatekey(crypto.FILETYPE_PEM, privkey)
        except crypto.Error:
            return "Invalid privkey provided."

        # Check if fullchain and privkey match
        try:
            context = SSL.Context(SSL.TLSv1_METHOD)
            context.use_certificate(cert)
            context.use_privatekey(key)
            context.check_privatekey()
        except SSL.Error:
            return "Fullchain and privkey do not match."

        os.makedirs(f"{self.ssl_root}/{identifier}")
        with open(f"{self.ssl_root}/{identifier}/fullchain.pem", "w") as f:
            f.write(fullchain)
        with open(f"{self.ssl_root}/{identifier}/privkey.pem", "w") as f:
            f.write(privkey)

        # Get valid DNS names and retunr
