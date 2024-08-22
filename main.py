from fastapi import FastAPI, Request, staticfiles, APIRouter
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.responses import JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from extensions.apimodels import pagecontent
from dotenv import load_dotenv
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
load_dotenv()

from routers import hosts, logs, filemanagerapi, sslcertificatesapi


templates = Jinja2Templates(directory="templates")

app = FastAPI(
    redoc_url=None,
)

pages = APIRouter(
    prefix="",
    tags=["Pages API"],
)


@pages.get("/api/page/{page}")
async def get_page(page: pagecontent, request: Request):
    return templates.TemplateResponse(
        f"pages/{page.value}.j2",
        {
            "request": request,
        },
    )


@pages.get("/")
async def redirect():
    """
    Redirect to the home page.
    """
    return RedirectResponse(url="/page/home")


@pages.get("/page/{page}")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.j2",
        {"request": request},
    )


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


# Add routes & static files to the app
app.include_router(pages)
app.include_router(logs)
app.include_router(hosts)
app.include_router(filemanagerapi)
app.include_router(sslcertificatesapi)
app.mount("/", staticfiles.StaticFiles(directory="public"), name="public")
