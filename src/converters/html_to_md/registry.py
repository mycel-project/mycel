import importlib
import logging

from bs4 import BeautifulSoup

from src.converters.html_to_md.utils import gather_by_domain
from src.types.html_block import HtmlBlock
from src.types.html_content import HtmlContent
from src.types.md_content import MdContent


from .profile import Profile
from .profiles_config import PROFILES_ORDER


logger = logging.getLogger(__name__)


class HtmlToMdRegistry:
    def __init__(self) -> None:
        self._profiles: list[Profile] = []
        self._load_profiles()

    def route(self, html: HtmlContent) -> list[HtmlBlock]:
        soup = BeautifulSoup(html, "lxml")

        blocks = []

        for tag in soup.find_all(True):
            domain = str(tag.get("mycel-domain") or "generic")
            
            blocks.append(
                HtmlBlock(
                    domain=domain,
                    node=HtmlContent(tag)
                )
            )

        return blocks

    def convert(self, html: HtmlContent) -> MdContent:
        blocks = self.route(html)

        converters = {
            p.domain: p for p in self._profiles
        }

        results = []

        for domain, chunks in gather_by_domain(blocks):
            logger.debug(f"Running converter for domain {domain} ({len(chunks)} chunks)")

            converter = converters.get(domain)

            if not converter:
                continue

            # Handle gathering directtly in split_by_domain_run?
            html_fragments = "\n".join(str(b.node) for b in chunks)

            md = converter.convert(html_fragments)

            results.append(md)

        return MdContent(
            "\n".join(results)
        )

    def _load_profiles(self) -> None:
        for profile_name in PROFILES_ORDER:
            self._load_profile(profile_name)

    def _load_profile(self, profile_name: str) -> None:
        try:
            module = importlib.import_module(
                f".profiles.{profile_name}",
                package=__package__
            )

            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                if (
                    isinstance(attr, type)
                    and issubclass(attr, Profile)
                    and attr is not Profile
                ):
                    profile = attr()

                    self._register_profile(
                        profile
                    )

        except ImportError as e:
            raise ImportError(
                f"Error while loading profile '{profile_name}': {e}"
            )

    def _register_profile(
        self,
        profile: Profile,
    ) -> None:
        self._profiles.append(profile)
