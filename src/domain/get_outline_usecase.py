from src.core.regex import HEADING_PATTERN
from src.models.node import Node
from src.models.outline import Outline, OutlineEntry


class GetOutlineUseCase:
    def execute(self, node: Node) -> Outline:
        text = node.content.get_first_field() or "" if node.content else ""
        entries = []
        offset = 0
        for line in text.splitlines(keepends=True):
            match = HEADING_PATTERN.match(line)
            if match:
                entries.append(OutlineEntry(
                    level=len(match.group(1)),
                    title=match.group(2).strip(),
                    offset=offset,
                ))
            offset += len(line)
        return Outline(entries=entries)
