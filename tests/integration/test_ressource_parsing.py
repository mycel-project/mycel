from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.sources.registry import SourceRegistry


def test_html_to_md_clean_and_convert():
    with open("tests/fixtures/dog_from_mediawikiapi.html", "r") as f:
        data = f.read() # simulate fetch from web
    user_agent = "Mozilla/5.0"
    source_registry = SourceRegistry(user_agent)
    result = source_registry.clean(data)
    converter_registry = HtmlToMdRegistry()
    md = converter_registry.convert(result.cleaned_html)
    with open("draft/result.md", "w") as f:
        f.write(md)
