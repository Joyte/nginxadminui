from enum import Enum
from pydantic import BaseModel
from typing import Optional


class pagecontent(str, Enum):
    home = "home"
    hosts = "hosts"
    accesslists = "accesslists"
    sslcerts = "sslcerts"
    users = "users"
    auditlog = "auditlog"
    settings = "settings"


class CreateSiteContent(BaseModel):
    content: str


class EditSiteContent(BaseModel):
    content: Optional[str] | None = None
    filename: Optional[str] | None = None
