from src.ast.parsers.html_parser import HtmlParser

class TestParsing:
    def test_parsing(self):
        parser = HtmlParser()
        with open("html.html", "r") as f:
            html_doc=f.read()

        print()
        parser.parse(html_doc)
