from src.sources.registry import SourceRegistry


def test_fetch():
    user_agent = "Mozilla/5.0"
    source_registry = SourceRegistry(user_agent)
    html = source_registry.fetch("https://en.wikipedia.org/wiki/SuperMemo").html
    with open("tests/fixtures/supermemo_from_mediawikiapi.html", "w") as f:
        f.write(html)
