import json
import os
from pydantic import BaseModel
from enum import Enum

class MycelConfig(BaseModel):
    interface: str
    network_user_agent: str
    db_path: str
    log_level: str
    allow_private_urls_fetch: bool
    ensure_default_user: bool
    run_migrations_on_startup: bool = True

    @property
    def sqlalchemy_url(self) -> str:
        return build_db_url(self.db_path)

def build_db_url(db_path: str) -> str:
    path = os.getenv("DATABASE_URL") or db_path
    if str(path).startswith("postgresql"):
        return str(path)
    return f"sqlite:///{path}"

def load_config(config_file: str = "config.json") -> MycelConfig:
    with open(config_file, "r") as f:
        config_dict = json.load(f)
    return MycelConfig(**config_dict)

