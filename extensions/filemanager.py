from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

filemanager = APIRouter(
    prefix="/api/filemanager",
    tags=["File Manager API"],
)
