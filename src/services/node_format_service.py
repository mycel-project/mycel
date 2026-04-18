import re

from src.models.node import Node
from typing import Union

from src.utils.format import ensure_double_newline_left, ensure_double_newline_right


class NodeFormatService:
    def emphasize_region(self, node: Node, content: Union[str, dict]) -> Node:
        """
        No blockquote nesting supported at the moment
        """
        if isinstance(content, dict):
            raise ValueError(
                "Fragment creation from multiple node fields is not supported. "
                "Please fragment one field at a time."
            )

        content = content.strip()

        target_fields = [
            (k, v) for k, v in node.content.fields.items()
            if content in v
        ]

        if len(target_fields) == 0:
            raise ValueError("No field found.")
        if len(target_fields) > 1:
            raise ValueError("Content has been found in multiple fields.")

        key, field = target_fields[0]

        match = re.search(re.escape(content), field)
        if not match:
            raise ValueError("Content not found in field (unexpected).")

        start, end = match.span()

        before = field[:start]
        middle = field[start:end]
        after = field[end:]

        quoted = "\n".join(self.blockquote_line(line) for line in middle.split("\n"))

        before = ensure_double_newline_left(before.rstrip())
        after = ensure_double_newline_right(after.lstrip())

        new_field = before + quoted + after

        node.content.fields[key] = new_field
        return node

    def blockquote_line(self, line: str) -> str:
        stripped = line.lstrip()

        if stripped.startswith(">"):
            return stripped
        return "> " + stripped
