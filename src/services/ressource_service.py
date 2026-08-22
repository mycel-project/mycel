import subprocess
from src.converters.html_to_md.registry import HtmlToMdRegistry
from src.models.ressource import Ressource
from src.sources.registry import SourceRegistry

import logging
logger = logging.getLogger(__name__)

class RessourceService:
    def __init__(self, source_registry: SourceRegistry, html_to_md_registry: HtmlToMdRegistry):
        self._source_registry = source_registry
        self._htm_registry = html_to_md_registry

    def defuddle_convert(self, html: str) -> str:
        import os
        node_bin = "node"
        if os.path.exists("./env/bin/node"):
            node_bin = "./env/bin/node"
        elif os.path.exists("./env/Scripts/node.exe"):
            node_bin = "./env/Scripts/node.exe"

        result = subprocess.run(
            [node_bin, "./node_deps/node_modules/defuddle/dist/cli.js",
             "parse", "--markdown"],
            input=html,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            logger.error(f"Defuddle failed (exit {result.returncode}): {result.stderr}")
            raise RuntimeError(f"Defuddle conversion failed: {result.stderr}")
        return result.stdout

    def get_ressource_from_url(self, url: str) -> Ressource:
        fetched = self._source_registry.fetch(url)
        html = fetched.html
        title = fetched.title

        markdown = self.defuddle_convert(html)
        # Testing with defuddle for now to extract Markdown
#        cleaned = self._source_registry.clean(html)
#        markdown = self._htm_registry.convert(cleaned.cleaned_html)
        return Ressource(
            title=title,
            content=markdown,
            source=url
        )
