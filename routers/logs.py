from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from extensions.database import Logs, get_db, Session
from extensions.apimodels import (
    Log,
    LogType,
    ServerLogType,
    LogUIHeaders,
    LogAccessHeaders,
    LogErrorHeaders,
)
from extensions.logmanager import LogManager, LogException


logs = APIRouter(
    prefix="/api/logs",
    tags=["Logs API"],
)

logmanager = LogManager()


@logs.get("")
async def get_log_names():
    """
    Get all log names, including a fake log name for the server database-based log.
    """
    return {**{"server": ["ui"]}, **logmanager.get_logs()}


@logs.post("")
async def create_log(log: Log, db: Session = Depends(get_db)):
    """
    Create a new log.
    """
    # Check if log type already exists
    try:
        logmanager.get_log(log, limit=1, offset=0)
        return JSONResponse(
            content={"message": "Log type already exists."}, status_code=400
        )
    except LogException as e:
        if str(e) != "Log not found.":
            raise e

    logmanager.create_log(log)

    db.add(Logs(importance=1, value=f"Created a new log type `{log.name}`."))
    db.commit()

    return JSONResponse(
        content={"message": "Log type created.", "types": LogType._member_names_},
        status_code=201,
    )


@logs.get("/server/{type}.log")
async def get_server_log(
    type: ServerLogType,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get the server based log, limited to defined amount (default 100), offset by defined amount (default 0).
    Ordered chronologically.
    """
    match type:
        case ServerLogType.ui:
            data = (
                db.query(Logs)
                .order_by(Logs.id.desc())
                .limit(limit)
                .offset(offset)
                .all()
            )
            return {
                "headers": [header.value for header in LogUIHeaders],
                "data": [
                    {
                        "importance": log.importance,
                        "python_time": str(log.id),
                        "message": log.value,
                    }
                    for log in data
                ],
            }
        case _:
            return JSONResponse(
                content={"message": "Log type not found."}, status_code=404
            )


@logs.get("/{name}/{type}.log")
async def get_logs(
    name: str,
    type: LogType,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Get all logs, limited to defined amount (default 100), offset by defined amount (default 0).
    Ordered chronologically.
    """
    try:
        data = logmanager.get_log(Log(name=name, type=type), limit, offset)
    except LogException as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)

    match type:
        case LogType.access:
            headers = [header.value for header in LogAccessHeaders]
        case LogType.error:
            headers = [header.value for header in LogErrorHeaders]

    return {"headers": headers, "data": data}


@logs.delete("/{name}")
async def delete_log(name: str, db: Session = Depends(get_db)):
    """
    Delete a log type.
    """
    try:
        logmanager.delete_log(Log(name=name))
    except LogException as e:
        return JSONResponse(content={"message": str(e)}, status_code=404)

    db.add(Logs(importance=1, value=f"Deleted the log type `{name}`."))
    db.commit()

    return JSONResponse(content={"message": "Log type deleted."}, status_code=200)
