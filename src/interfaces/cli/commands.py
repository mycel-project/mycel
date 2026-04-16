import click

from src.services.collection_service import CollectionService
from src.services.node_service import NodeService
from src.services.ressource_service import RessourceService
from src.services.review_service import ReviewService


def create_cli_group(node_service: NodeService, collection_service: CollectionService, review_service: ReviewService, ressource_service: RessourceService, bus):    
    @click.group()
    def cli():
        pass
        
    @cli.command(
    help="""
    Fetch a web resource from a URL.

    Example:
      mycel get https://en.wikipedia.org/wiki/Python
    """
    )
    @click.argument("url")
    def get(url):
        ressource = ressource_service.get_ressource_from_url(url)
        click.echo(ressource["markdown"])

    return cli
