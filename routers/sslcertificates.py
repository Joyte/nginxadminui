from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from extensions.database import get_db, Session, Logs
from extensions.apimodels import Certificate
from extensions import SSLCertificates
from os import getenv

sslcertificatesapi = APIRouter(
    prefix="/api/sslcertificates",
    tags=["SSL Certificates API"],
)

sslcertificates = SSLCertificates()


@sslcertificatesapi.get("")
async def list_sslcertificates():
    return sslcertificates.list_certificates()


@sslcertificatesapi.get("/{site}")
async def get_sslcertificate(site: str):
    return sslcertificates.get_certificate(site)


@sslcertificatesapi.post("/{site}")
async def create_sslcertificate(
    site: str, certificate: Certificate, db: Session = Depends(get_db)
):
    sslcertificates.create_certificate(site, certificate.fullchain, certificate.privkey)

    db.add(
        Logs(
            importance=1,
            value=f"Created a new SSL certificate for `{site}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={"message": "Certificate created successfully."},
    )


@sslcertificatesapi.put("/{site}")
async def replace_sslcertificate(
    site: str, certificate: Certificate, db: Session = Depends(get_db)
):
    sslcertificates.replace_certificate(
        site, certificate.fullchain, certificate.privkey
    )

    db.add(
        Logs(
            importance=1,
            value=f"Replaced the SSL certificate for `{site}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={"message": "Certificate replaced successfully."},
    )


@sslcertificatesapi.delete("/{site}")
async def delete_sslcertificate(site: str, db: Session = Depends(get_db)):
    sslcertificates.delete_certificate(site)

    db.add(
        Logs(
            importance=1,
            value=f"Deleted the SSL certificate for `{site}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={"message": "Certificate deleted successfully."},
    )
