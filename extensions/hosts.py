from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from configinteraction.apimodels import CreateSiteContent, EditSiteContent
from extensions.nginxconfig import NginxConfig
from database.hosts import Data, Logs, get_db, Session
import time
from os import getenv

nginxconfig = NginxConfig(
    getenv("SITES_AVAILABLE", "/etc/nginx/sites-available"),
    getenv("SITES_ENABLED", "/etc/nginx/sites-enabled"),
)

hosts = APIRouter(
    prefix="/api/hosts",
    tags=["Hosts"],
)


def set_nginxreload(db: Session):
    if not db.query(Data).filter(Data.id == "nginxreload").first():  # type: ignore
        db.add(Data(id="nginxreload", bool=True))
        db.commit()


@hosts.get("/reload")
async def checkreload(db: Session = Depends(get_db)):
    """
    Check if nginx needs to be reloaded.
    """
    if db.query(Data).filter(Data.id == "nginxreload").first():  # type: ignore
        return {"reload": True}

    return {"reload": False}


@hosts.post("/reload")
async def reloadnginx(db: Session = Depends(get_db)):
    """
    Reload the nginx service.
    """
    result = nginxconfig.reload_nginx()
    if result == True:
        db.add(
            Logs(
                id=time.strftime("%Y-%m-%d %H:%M:%S"),
                importance=1,
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
        Logs(
            id=time.strftime("%Y-%m-%d %H:%M:%S"),
            importance=3,
            value="Nginx failed to reload: " + str(result),
        )
    )
    return JSONResponse(
        content={
            "message": str(result),
        },
        status_code=400,
    )


@hosts.get("")
async def getsites():
    return {"sites": nginxconfig.list_files()}


@hosts.get("/{filename}")
async def getsite(filename: str):
    return {"content": nginxconfig.get_file(filename)}


@hosts.post("/{filename}")
async def createsite(
    filename: str, data: CreateSiteContent, db: Session = Depends(get_db)
):
    nginxconfig.create_site(filename, data.content)
    set_nginxreload(db)
    return {"message": "Site created successfully"}


@hosts.put("/{filename}")
async def editsite(filename: str, data: EditSiteContent, db: Session = Depends(get_db)):
    if data.content:
        nginxconfig.edit_file(filename, data.content)

    if data.filename:
        nginxconfig.rename_file(filename, data.filename)

    set_nginxreload(db)

    return {"message": "Site edited successfully"}


@hosts.delete("/{filename}")
async def deletesite(filename: str, db: Session = Depends(get_db)):
    nginxconfig.delete_site(filename)
    set_nginxreload(db)
    return {"message": "Site deleted successfully"}


@hosts.get("/{filename}/enabled")
async def checksiteenabled(filename: str):
    return {"enabled": nginxconfig.check_site_enabled(filename)}


@hosts.put("/{filename}/enabled")
async def togglesite(filename: str, enabled: bool, db: Session = Depends(get_db)):
    if enabled:
        nginxconfig.enable_site(filename)
    else:
        nginxconfig.disable_site(filename)

    set_nginxreload(db)

    return {"message": "Site enabled successfully"}
