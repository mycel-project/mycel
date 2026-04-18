import re
from typing import Optional

from src.models.node import Node
from src.models.node_content import NodeContent
from src.types.text_segment import TextSegment
from src.utils.debug import preview_extract
from src.utils.format import ensure_double_newline_left, ensure_double_newline_right


class NodeFormatService:

    def inline_region(
        self,
        node: Node,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None
    ) -> Node:
        segment = self.get_content_portions(
            node.content,
            field,
            start,
            end,
            expected_text
        )

        cleaned_target = segment.target.replace("`", "")

        node.content.fields[field] = (
            segment.before + "`" + cleaned_target + "`" + segment.after
        )

        return node

    def blockquote_region(
        self,
        node: Node,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None
    ) -> Node:
        segment = self.get_content_portions(
            node.content,
            field,
            start,
            end,
            expected_text
        )

        quoted = "\n".join(
            self.blockquote_line(line) for line in segment.target.split("\n")
        )

        before = ensure_double_newline_left(segment.before.rstrip())
        after = ensure_double_newline_right(segment.after.lstrip())

        node.content.fields[field] = before + quoted + after

        return node

    def get_content_portions(
        self,
        node_content: NodeContent,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None
    ) -> TextSegment:

        if field not in node_content.fields:
            raise ValueError(f"Field '{field}' not found in node content")

        text = node_content.fields[field]

        if start < 0 or end > len(text) or start >= end:
            raise ValueError("Invalid selection range")

        selected = text[start:end]

        if expected_text is not None and selected != expected_text:
            raise ValueError(
                "Selection mismatch (outdated state or tampered data). "
                f"Expected: '{preview_extract(expected_text)}' | "
                f"Received: '{preview_extract(selected)}' | "
            )

        return TextSegment(
            text[:start],
            selected,
            text[end:]
        )

    def blockquote_line(self, line: str) -> str:
        stripped = line.lstrip()

        if stripped.startswith(">"):
            return stripped

        return "> " + stripped
