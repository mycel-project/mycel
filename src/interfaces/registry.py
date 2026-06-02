from .rest.rest import Rest
from .cli.cli import Cli

INTERFACE_REGISTRY = {
    "rest": Rest,
    "cli": Cli,
}
