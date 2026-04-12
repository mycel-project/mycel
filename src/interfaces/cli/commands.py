import click


def create_cli_group(node_service, collection_service, review_service, ressource_service, bus):    
    @click.group()
    def cli():
        pass
        
    @cli.command()
    def wiki():
        ressource_service.fetch_from_wikipedia("https://fr.wikipedia.org/wiki/Berger_allemand")
        
    return cli
