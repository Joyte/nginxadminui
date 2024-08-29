from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from extensions.database import get_db, Session, Logs
from extensions.apimodels import Certificate, Domain
from extensions import SSLCertificates
from os import getenv
import random
import string

sslcertificatesapi = APIRouter(
    prefix="/api/sslcertificates",
    tags=["SSL Certificates API"],
)

sslcertificates = SSLCertificates()


@sslcertificatesapi.get("")
async def list_sslcertificates():
    return sslcertificates.list_certificates()


@sslcertificatesapi.get("/{identifier}")
async def get_sslcertificate(identifier: str):
    return sslcertificates.get_certificate(identifier)


@sslcertificatesapi.post("")
async def create_sslcertificate(
    certificate: Certificate, db: Session = Depends(get_db)
):
    # 8 chars long lowercase & digits
    identifier = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))

    result = sslcertificates.create_certificate(
        identifier, certificate.fullchain, certificate.privkey
    )

    if result:
        return JSONResponse(
            content={"message": result},
            status_code=400,
        )

    valid_domains = sslcertificates.get_certificate(identifier)["valid_sites"]

    db.add(
        Logs(
            importance=1,
            value=f"Created a new SSL certificate with identifier `{identifier}` for the following domains: {', '.join(valid_domains)}",
        )
    )

    db.commit()
    return JSONResponse(
        content={
            "message": "Certificate created successfully.",
            "identifier": "identifier",
            "valid_domains": valid_domains,
        },
    )


@sslcertificatesapi.put("")
async def generate_sslcertificate(domain: Domain, db: Session = Depends(get_db)):
    identifier = sslcertificates.generate_certificate(domain.domain)

    db.add(
        Logs(
            importance=1,
            value=f"Generated self-signed SSL certificate for `{domain.domain}`, with identifier `{identifier}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={
            "message": "Certificate generated successfully.",
            "identifier": identifier,
        },
    )


@sslcertificatesapi.delete("/{identifier}")
async def delete_sslcertificate(identifier: str, db: Session = Depends(get_db)):
    sslcertificates.delete_certificate(identifier)

    db.add(
        Logs(
            importance=1,
            value=f"Deleted the SSL certificate for `{identifier}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={"message": "Certificate deleted successfully."},
    )
