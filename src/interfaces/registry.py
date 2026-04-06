from .websocket.web import Web
from .rest.rest import Rest

INTERFACE_REGISTRY = {
    "websocket": Web,
    "rest": Rest,
}
