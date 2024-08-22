from enum import Enum
from pydantic import BaseModel
from typing import Optional


class pagecontent(str, Enum):
    home = "home"
    hosts = "hosts"
    filemanager = "filemanager"
    accesslists = "accesslists"
    sslcertificates = "sslcertificates"
    users = "users"
    logs = "logs"
    settings = "settings"


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
