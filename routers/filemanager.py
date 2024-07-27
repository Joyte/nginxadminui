from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

filemanager = APIRouter(
    prefix="/api/filemanager",
    tags=["File Manager API"],
)


@filemanager.get("/list")
async def list_files():
    pass
