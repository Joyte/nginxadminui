from enum import Enum
from pydantic import BaseModel
from typing import Optional


class pagecontent(str, Enum):
    home = "home"
    hosts = "hosts"
    filemanager = "filemanager"
    sslcertificates = "sslcertificates"
    logs = "logs"
    php = "php"


class CreateSiteContent(BaseModel):
    content: str


class EditSiteContent(BaseModel):
    content: Optional[str] | None = None
    filename: Optional[str] | None = None


class FilesList(BaseModel):
    files: list[str]


class Certificate(BaseModel):
    fullchain: str
    privkey: str


class Domain(BaseModel):
    domain: str


class LogType(str, Enum):
    access = "access"
    error = "error"


class ServerLogType(str, Enum):
    ui = "ui"


class LogUIHeaders(str, Enum):
    time = "Time"
    message = "Message"


class LogAccessHeaders(str, Enum):
    remote_addr = "Remote Address"
    remote_user = "Remote User"
    time_local = "Time"
    request = "Request"
    status = "Status"
    body_bytes_sent = "Body Bytes Sent"
    http_referer = "HTTP Referer"
    http_user_agent = "User Agent"


class LogErrorHeaders(str, Enum):
    date = "Date"
    time = "Time"
    log_level = "Log Level"
    pid = "PID"
    tid = "TID"
    cid = "CID"
    message = "Message"


class LogErrorLevel(str, Enum):
    debug = "1"
    info = "1"
    notice = "1"
    warn = "3"
    error = "3"
    crit = "3"
    alert = "3"
    emerg = "3"


class Command(BaseModel):
    command: str


class Log(BaseModel):
    name: str
    type: Optional[LogType] | None = None
