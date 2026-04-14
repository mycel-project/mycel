from src.services.ressource_service import RessourceService
from src.sources.registry import SourceRegistry

class TestCleaner:
    def test_cleaner(self):        
        user_agent = "Mozilla/5.0"
        with open("tests/fixtures/dog_from_mediawikiapi.html", "r") as f:
            data = f.read()
        source_registry = SourceRegistry(user_agent)
        
        source_registry.clean(data)
