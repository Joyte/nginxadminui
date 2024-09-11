from fastapi import APIRouter, Depends, UploadFile
from starlette.responses import JSONResponse
from extensions.filemanager import Filemanager
from extensions.database import get_db, Session, Logs
from extensions.apimodels import FilesList, Command

filemanagerapi = APIRouter(
    prefix="/api/filemanager",
    tags=["File Manager API"],
)

filemanager = Filemanager()


@filemanagerapi.get("")
async def list_files(path: str = ""):
    if ".." in path:
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid path."},
        )
    return filemanager.list_files(path)


@filemanagerapi.get("/download/{path:path}")
async def download_file(path: str):
    file = filemanager.get_file(path)
    if file is None:
        return JSONResponse(
            status_code=404,
            content={"message": "File not found."},
        )
    return file


@filemanagerapi.put("/edit/{path:path}")
async def edit_file(path: str, file: UploadFile, db: Session = Depends(get_db)):
    filemanager.replace_file(path, file)

    db.add(
        Logs(
            importance=1,
            value=f"Edited a file named `{path}`",
        )
    )
    db.commit()
    return JSONResponse(
        content={"message": "File edited successfully."},
    )


@filemanagerapi.post("/composer/{path:path}")
async def composer(path: str, db: Session = Depends(get_db)):
    response = filemanager.composer(path)

    db.add(
        Logs(
            importance=1,
            value=f"Ran composer at `{path}` with response `{response}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={"message": "Command ran.", "response": response},
    )


@filemanagerapi.post("/unzip/{path:path}")
async def unzip_file(path: str, files: FilesList, db: Session = Depends(get_db)):
    for name in files.files:
        response = filemanager.unzip_file(path, name)

        if response is not None:
            db.add(
                Logs(
                    importance=3,
                    value=f"Failed to unzip a file named `{name}` at `{path}`",
                )
            )
            db.commit()
            return JSONResponse(
                status_code=400,
                content={"message": response},
            )

    db.add(
        Logs(
            importance=1,
            value=f"Unzipped files named `{files.files}` at `{path}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={"message": "File unzipped successfully."},
    )


@filemanagerapi.get("/{path:path}")
async def get_file(path: str):
    file = filemanager.get_file(path)
    if file is None:
        return JSONResponse(
            status_code=404,
            content={"message": "File not found."},
        )
    return file


@filemanagerapi.delete("/{path:path}/")
async def delete_folder(path: str, db: Session = Depends(get_db)):
    filemanager.delete_folder(path)

    db.add(
        Logs(
            importance=1,
            value=f"Deleted a folder named `{path}`",
        )
    )
    db.commit()
    return JSONResponse(
        content={"message": "Folder deleted successfully."},
    )


@filemanagerapi.delete("/{path:path}")
async def delete_files(path: str, data: FilesList, db: Session = Depends(get_db)):

    for file in data.files:
        filemanager.delete_file(path, file)

    db.add(
        Logs(
            importance=1,
            value=f"Deleted files named `{data.files}` at `{path}`",
        )
    )
    db.commit()
    return JSONResponse(
        content={"message": "File deleted successfully."},
    )


@filemanagerapi.post("/{path:path}")
async def create_file(
    path: str, files: list[UploadFile], db: Session = Depends(get_db)
):

    for file in files:
        filemanager.create_file(path, file)

    db.add(
        Logs(
            importance=1,
            value=f"Created files named `{[file.filename for file in files]}` at `{path}`",
        )
    )

    db.commit()
    return JSONResponse(
        content={"message": "File created successfully."},
    )


@filemanagerapi.put("/{path:path}")
async def create_folder(path: str, db: Session = Depends(get_db)):
    filemanager.create_folder(path)
    db.add(
        Logs(
            importance=1,
            value=f"Created a folder named `{path}`",
        )
    )
    db.commit()
    return JSONResponse(
        content={"message": "Folder created successfully."},
    )
