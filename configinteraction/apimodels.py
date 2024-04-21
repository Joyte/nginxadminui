from enum import Enum
from pydantic import BaseModel


class pagecontent(str, Enum):
    home = "home"
    hosts = "hosts"
    accesslists = "accesslists"
    sslcerts = "sslcerts"
    users = "users"
    auditlog = "auditlog"
    settings = "settings"


class ContentInBody(BaseModel):
    content: str
