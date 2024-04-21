from fastapi import FastAPI, Request, staticfiles, APIRouter
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from configinteraction.apimodels import pagecontent, EditSiteUpdate
from library.nginxconfig import NginxConfig
from dotenv import load_dotenv
from os import getenv

load_dotenv()

templates = Jinja2Templates(directory="templates")
nginxconfig = NginxConfig(
    getenv("SITES_AVAILABLE", "/etc/nginx/sites-available"),
    getenv("SITES_ENABLED", "/etc/nginx/sites-enabled"),
)

app = FastAPI(
    # docs_url=None,
    redoc_url=None,
    # openapi_url=None,
)

nginx = APIRouter(
    prefix="/api/nginx",
    tags=["nginx"],
)


@app.get("/api/page/{page}")
async def getpage(page: pagecontent, request: Request):
    return templates.TemplateResponse(
        f"pages/{page.value}.j2",
        {
            "request": request,
        },
    )


@app.get("/")
async def redirect():
    """
    Redirect to the home page.
    """
    return RedirectResponse(url="/page/home")


@app.get("/page/{page}")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.j2",
        {"request": request},
    )


@nginx.get("/sites")
async def getsites():
    return {"sites": nginxconfig.list_files()}


@nginx.get("/site/{filename}")
async def getsite(filename: str):
    return {"content": nginxconfig.get_file(filename)}


@nginx.post("/site/{filename}")
async def createsite(filename: str, content: str):
    nginxconfig.create_site(filename, content)
    return {"message": "Site created successfully"}


@nginx.put("/site/{filename}")
async def editsite(filename: str, data: EditSiteUpdate):
    nginxconfig.edit_file(filename, data.content)
    return {"message": "Site edited successfully"}


@nginx.delete("/site/{filename}")
async def deletesite(filename: str):
    nginxconfig.delete_site(filename)
    return {"message": "Site deleted successfully"}


@nginx.get("/site/{filename}/enabled")
async def checksiteenabled(filename: str):
    return {"enabled": nginxconfig.check_site_enabled(filename)}


@nginx.put("/site/{filename}/enabled")
async def togglesite(filename: str, enabled: bool):
    if enabled:
        nginxconfig.enable_site(filename)
    else:
        nginxconfig.disable_site(filename)

    return {"message": "Site enabled successfully"}


# Add error handling for any exceptions
@app.exception_handler(500)
@app.exception_handler(StarletteHTTPException)
async def exception_handler(request: Request, exc: StarletteHTTPException):
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            content={
                "code": getattr(exc, "status_code", 500),
                "message": getattr(exc, "detail", "Internal Server Error"),
            },
            status_code=getattr(exc, "status_code", 500),
        )

    return templates.TemplateResponse(
        "error.j2",
        {
            "request": request,
            "code": getattr(exc, "status_code", 500),
            "message": getattr(exc, "detail", "Internal Server Error"),
        },
        status_code=getattr(exc, "status_code", 500),
    )


# Add static files to the app
app.include_router(nginx)
app.mount("/", staticfiles.StaticFiles(directory="public"), name="public")
