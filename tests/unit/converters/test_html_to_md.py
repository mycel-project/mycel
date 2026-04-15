from src.converters.html_to_md.profiles.generic import GenericConverter
from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.types.html_content import HtmlContent


def test_html_to_md():
    with open("tests/fixtures/supermemo_from_mediawikiapi.html", "r") as f:
        data = f.read()
    HtmlContent(data)
#    converter = GenericConverter()
#    md = converter.convert(data)
    registry = HtmlToMdRegistry()
    md = registry.convert(data)
    with open("draft/result.md", "w") as f:
        f.write(md)
