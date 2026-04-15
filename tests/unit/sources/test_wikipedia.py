from src.sources.wikipedia import WikipediaCleaner

class TestWikipedia:
    def test_cleaner(self):
        cleaner = WikipediaCleaner()
        result = cleaner.clean("salut")
        print(result.cleaned_html)
