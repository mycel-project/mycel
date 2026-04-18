import re
from typing import Optional
import re

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
    

    def cloze_region(
        self,
        node: Node,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None,
        cloze_index: Optional[int] = 1,
    ) -> Node:
        cloze_index = 1 # just support one at the moment
        segment = self.get_content_portions(
            node.content,
            field,
            start,
            end,
            expected_text
        )
        cleaned_target = segment.target.replace("{{", "((").replace("}}", "))")
        node.content.fields[field] = (
            segment.before + "{{c" + str(cloze_index) + "::" + cleaned_target + "}}" + segment.after
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
    

    def unquote_line(self, line: str, allowed_prefix_pattern: Optional[str] = None) -> str:
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


    def remove_blockquote_formatting(
        self,
        text: str,
        allowed_prefix_pattern: Optional[str] = None
    ) -> str:
        """
        If an allowed_prefix_pattern is provided, the function will ignore this prefix
        when detecting and removing blockquote markers. This allows handling cases where
        a blockquote appears after a specific leading pattern (e.g. cloze syntax like "{{c1::").
        """
        lines = text.split("\n")

        cleaned_lines = [
            self.unquote_line(line, allowed_prefix_pattern)
            for line in lines
        ]

        return "\n".join(cleaned_lines)

    
    def remove_inline_code_formatting(self, text: str) -> str:
        return text.replace("`", "")
