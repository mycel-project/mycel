from .websocket.web import Web
from .rest.rest import Rest
from .cli.cli import Cli

INTERFACE_REGISTRY = {
    "websocket": Web,
    "rest": Rest,
    "cli": Cli,
}
