import click


def create_cli_group(node_service, collection_service, review_service, ressource_service, bus):    
    @click.group()
    def cli():
        pass
    
    @cli.command()
    def hello():
        print("hello")
                
    return cli
