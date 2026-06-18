from pydantic import BaseModel
from enum import Enum

class MycelConfig(BaseModel):
    interface: str
    network_user_agent: str
    db_path: str
    log_level: str
    allow_private_urls_fetch: bool
    ensure_default_user: bool

