from pydantic import BaseModel
from enum import Enum

class DeploymentMode(str, Enum):
    SELF_HOSTED = "self-hosted"
    CLOUD = "cloud"

class MycelConfig(BaseModel):
    interface: str
    network_user_agent: str
    db_path: str
    log_level: str
    deployment_mode: DeploymentMode = DeploymentMode.SELF_HOSTED
    allow_private_urls_fetch: bool

