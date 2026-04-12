from ..parser import Parser


class WikipediaParser(Parser):
    def can_parse(self, content: str) -> bool:
        return "mw-parser-output" in content

    def parse(self, content: str) -> dict:
        return {"content": "not implemented"}
