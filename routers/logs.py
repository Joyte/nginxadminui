from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse
from extensions.database import Logs, get_db, Session

logs = APIRouter(
    prefix="/api/logs",
    tags=["Logs API"],
)


@logs.get("")
async def get_logs(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
    """
    Get all logs, limited to defined amount (default 100), offset by defined amount (default 0).
    Ordered chronologically.
    """
    return db.query(Logs).order_by(Logs.id.desc()).limit(limit).offset(offset).all()  # type: ignore
