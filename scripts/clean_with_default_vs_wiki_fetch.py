from src.sources.default_html import DefaultHtmlCleaner
import os

result_path = "results"
os.makedirs(result_path, exist_ok=True)

cleaner = DefaultHtmlCleaner()
with open("tests/fixtures/dog_from_mediawikiapi.html","r") as f:
    content = f.read()
result = cleaner.clean(content)
with open(f"{result_path}/cleaned_dog_from_wiki.html","w") as f:
    f.write(result.cleaned_html)

with open("tests/fixtures/dog_from_requests.html","r") as f:
    content = f.read()
result = cleaner.clean(content)
with open(f"{result_path}/cleaned_dog_from_requests.html","w") as f:
    f.write(result.cleaned_html)
