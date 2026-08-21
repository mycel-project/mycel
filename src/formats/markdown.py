import re
from typing import Pattern

from src.formats.base_format import BaseFormat
from src.models.outline import Outline, OutlineEntry

_HEADING_PATTERN = re.compile(r'^ {0,3}(#{1,6})(?:[ \x09\x0b\x0c](.*?))?(?:\s+#+\s*)?$', re.MULTILINE)
_BLOCKQUOTE_PATTERN = re.compile(r"^[ ]{0,3}>[ \t]?", re.MULTILINE)
_INLINE_CODE_PATTERN = re.compile(r"`([^`]+)`")

class MarkdownFormat(BaseFormat):
    id = "markdown"
    
    # --- OUTLINE ---

    @property
    def heading_pattern(self) -> Pattern[str]:
        return _HEADING_PATTERN

    def get_outline(self, text: str) -> Outline:
        entries = []
        offset = 0
        for line in text.splitlines(keepends=True):
            stripped = self.fragment_emphasis_pattern.sub('', line).lstrip()
            match = self.heading_pattern.match(stripped)
            if match:
                entries.append(OutlineEntry(
                    level=len(match.group(1)),
                    title=match.group(2).strip() if match.group(2) else "",
                    offset=offset,
                ))
            offset += len(line)
        return Outline(entries=entries)

    # --- FRAGMENT EMPHASIS (Blockquotes) ---

    @property
    def fragment_emphasis_pattern(self) -> Pattern[str]:
        return _BLOCKQUOTE_PATTERN

    def apply_fragment_emphasis(self, text: str) -> str:
        return "\n".join(self._blockquote_line(line) for line in text.split("\n"))

    def _blockquote_line(self, line: str) -> str:
        stripped = line.lstrip()
        if stripped.startswith(">"):
            return stripped
        return "> " + stripped

    def remove_fragment_emphasis(self, text: str, allowed_prefix_pattern: str | None = None) -> str:
        lines = text.split("\n")
        cleaned_lines = [self._unquote_line(line, allowed_prefix_pattern) for line in lines]
        return "\n".join(cleaned_lines)

    def _unquote_line(self, line: str, allowed_prefix_pattern: str | None = None) -> str:
        working_line = line
        if allowed_prefix_pattern:
            match = re.match(allowed_prefix_pattern, line)
            if match:
                working_line = line[match.end():]

        stripped = working_line.lstrip()
        has_removed = False
        while stripped.startswith(">"):
            stripped = stripped[1:].lstrip()
            has_removed = True

        if has_removed:
            prefix = line[:len(line) - len(working_line)]
            return prefix + stripped
        return line

    # --- SPORE EMPHASIS (Inline code) ---

    @property
    def spore_emphasis_pattern(self) -> Pattern[str] | None:
        return _INLINE_CODE_PATTERN

    def apply_spore_emphasis(self, text: str) -> str:
        cleaned = text.replace("`", "")
        return f"`{cleaned}`"

    def remove_spore_emphasis(self, text: str) -> str:
        return text.replace("`", "")

    # --- LINKS ---
    
    def strip_links(self, text: str) -> str:
        result = []
        i = 0
        while i < len(text):
            if text[i] == '[':
                j = text.find('](', i)
                if j == -1:
                    result.append(text[i:])
                    break
                link_text = text[i+1:j]
                k = j + 2
                depth = 1
                while k < len(text) and depth > 0:
                    if text[k] == '(':
                        depth += 1
                    elif text[k] == ')':
                        depth -= 1
                    k += 1
                result.append(link_text)
                i = k
            else:
                result.append(text[i])
                i += 1
        return ''.join(result)
