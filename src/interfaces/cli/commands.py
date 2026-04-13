import click


def create_cli_group(node_service, collection_service, review_service, ressource_service, bus):    
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
        click.echo(ressource["html"])

    return cli
