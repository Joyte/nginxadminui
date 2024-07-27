from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from extensions.apimodels import CreateSiteContent, EditSiteContent
from extensions import NginxConfig
from extensions.database import Data, Logs, get_db, Session
import time
from os import getenv

nginxconfig = NginxConfig(
    getenv("SITES_AVAILABLE", "/etc/nginx/sites-available"),
    getenv("SITES_ENABLED", "/etc/nginx/sites-enabled"),
)

hosts = APIRouter(
    prefix="/api/hosts",
    tags=["Hosts API"],
)


def set_nginx_reload(db: Session):
    if not db.query(Data).filter(Data.id == "nginxreload").first():  # type: ignore
        db.add(Data(id="nginxreload", is_active=True))  # type: ignore
        db.commit()


@hosts.get("/reload")
async def check_reload(db: Session = Depends(get_db)):
    """
    Check if nginx needs to be reloaded.
    """
    if db.query(Data).filter(Data.id == "nginxreload").first():  # type: ignore
        return {"reload": True}

    return {"reload": False}


@hosts.post("/reload")
async def reload_nginx(db: Session = Depends(get_db)):
    """
    Reload the nginx service.
    """
    result = nginxconfig.reload_nginx()
    if result == True:
        db.add(
            Logs(  # type: ignore
                id=time.strftime("%Y-%m-%d %H:%M:%S"),
                importance=2,
                value="Nginx successfully reloaded",
            )
        )
        # Check if data has nginxreload
        data = db.query(Data).filter(Data.id == "nginxreload").first()  # type: ignore
        if data:
            db.delete(data)
            db.commit()
        return {"message": "Nginx reloaded successfully"}

    db.add(
        Logs(  # type: ignore
            id=time.strftime("%Y-%m-%d %H:%M:%S"),
            importance=3,
            value="Nginx failed to reload: " + str(result),
        )
    )
    db.commit()
    return JSONResponse(
        content={
            "message": str(result),
        },
        status_code=400,
    )


@hosts.get("")
async def get_sites():
    return {"sites": nginxconfig.list_files()}


@hosts.get("/{filename}")
async def get_site(filename: str):
    return {"content": nginxconfig.get_file(filename)}


@hosts.post("/{filename}")
async def create_site(
    filename: str, data: CreateSiteContent, db: Session = Depends(get_db)
):
    nginxconfig.create_site(filename, data.content)
    set_nginx_reload(db)
    return {"message": "Site created successfully"}


@hosts.put("/{filename}")
async def edit_site(
    filename: str, data: EditSiteContent, db: Session = Depends(get_db)
):
    if data.content:
        nginxconfig.edit_file(filename, data.content)

    if data.filename:
        nginxconfig.rename_file(filename, data.filename)

    set_nginx_reload(db)

    return {"message": "Site edited successfully"}


@hosts.delete("/{filename}")
async def delete_site(filename: str, db: Session = Depends(get_db)):
    nginxconfig.delete_site(filename)
    set_nginx_reload(db)
    return {"message": "Site deleted successfully"}


@hosts.get("/{filename}/enabled")
async def check_site_enabled(filename: str):
    return {"enabled": nginxconfig.check_site_enabled(filename)}


@hosts.put("/{filename}/enabled")
async def toggle_site(filename: str, enabled: bool, db: Session = Depends(get_db)):
    if enabled:
        nginxconfig.enable_site(filename)
    else:
        nginxconfig.disable_site(filename)

    set_nginx_reload(db)

    return {"message": "Site enabled successfully"}
