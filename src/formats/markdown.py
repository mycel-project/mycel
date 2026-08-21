import re
from typing import Pattern

from src.formats.base_format import BaseFormat
from src.models.outline import Outline, OutlineEntry

_HEADING_PATTERN = re.compile(r'^ {0,3}(#{1,6})(?:[ \x09\x0b\x0c](.*?))?(?:\s+#+\s*)?$', re.MULTILINE)
_BLOCKQUOTE_PATTERN = re.compile(r"^[ ]{0,3}>[ \t]?", re.MULTILINE)

class MarkdownFormat(BaseFormat):
    id = "markdown"
    
    @property
    def heading_pattern(self) -> Pattern[str]:
        return _HEADING_PATTERN

    @property
    def extract_emphasis_pattern(self) -> Pattern[str]:
        return _BLOCKQUOTE_PATTERN

    def get_outline(self, text: str) -> Outline:
        entries = []
        offset = 0
        for line in text.splitlines(keepends=True):
            stripped = self.extract_emphasis_pattern.sub('', line).lstrip()
            match = self.heading_pattern.match(stripped)
            if match:
                entries.append(OutlineEntry(
                    level=len(match.group(1)),
                    title=match.group(2).strip() if match.group(2) else "",
                    offset=offset,
                ))
            offset += len(line)
        return Outline(entries=entries)
