import importlib
import logging
import uuid

from bs4 import BeautifulSoup

from src.types.html_content import HtmlContent
from src.types.md_content import MdContent


from .profile import Profile
from .profiles_config import PROFILES


logger = logging.getLogger(__name__)


class HtmlToMdRegistry:
    """
    Decompose html based on mycel-domain attributes, convert using the correct converter and reinject result by unsig text anchors (a more robust way must be implemented I guess)
    """
    def __init__(self) -> None:
        self._profiles: list[Profile] = []
        self._load_profiles()
        

    def extract_domains(self,html: HtmlContent):
        soup = BeautifulSoup(html, "lxml")

        extracts = {}

        for tag in soup.find_all(attrs={"mycel-domain": lambda v: v is not None}):
            anchor_id = str(uuid.uuid4())

            extracts[anchor_id] = tag

            placeholder = soup.new_tag("div")
            placeholder.string = f"mycel-anchor:{anchor_id}"

            tag.replace_with(placeholder)

        return extracts, soup
            
    def convert(self, html: HtmlContent) -> MdContent:
        extracts, soup = self.extract_domains(html)

        converters = {
            p.domain: p for p in self._profiles
        }

        results = []

        logger.debug(f"Running converter for domain generic ({len(str(soup))} chars)")
        base_md = converters["generic"].convert(str(soup))
        
        for anchor_id, extract in extracts.items():
            domain = extract.get("mycel-domain")
            logger.debug(f"Running converter for domain {domain} ({len(str(extract))} chars)")

            converter = converters.get(domain)

            if not converter:
                raise RuntimeError(f"No converter for domain {domain}")

            md = converter.convert(str(extract))

            base_md = base_md.replace(f"mycel-anchor:{anchor_id}", md)

        return MdContent(
            base_md
        )

    def _load_profiles(self) -> None:
        for profile_name in PROFILES:
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
