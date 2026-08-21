from typing import Optional

from src.formats.registry import get_format
from src.models.node import Node, NodeFields
from src.types.text_segment import TextSegment
from src.utils.debug import preview_extract
from src.utils.format import ensure_double_newline_left, ensure_double_newline_right

class NodeFormatService:
    
    # --- GENERAL (Mycel Logic) ---
    
    def build_cloze(self, text: str, index: int = 1) -> str:
        safe_text = text.replace("{{", "((").replace("}}", "))")
        return f"{{{{c{index}::{safe_text}}}}}"
    
    def get_content_portions(
        self,
        node_content: NodeFields,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None
    ) -> TextSegment:

        if field not in node_content:
            raise ValueError(f"Field '{field}' not found in node content")

        text = node_content[field]

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
    
    def cloze_region(
        self,
        node: Node,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None,
        cloze_index: int = 1, # just support one at the moment
    ) -> Node:

        segment = self.get_content_portions(
            node.fields,
            field,
            start,
            end,
            expected_text
        )

        cloze = self.build_cloze(segment.target, cloze_index)

        node.fields[field] = (
            segment.before + cloze + segment.after
        )

        return node

    # --- FORMAT DELEGATION ---
    
    def apply_spore_emphasis(
        self,
        node: Node,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None
    ) -> Node:

        segment = self.get_content_portions(
            node.fields,
            field,
            start,
            end,
            expected_text
        )

        formatter = get_format(node.data.content_format)
        inline = formatter.apply_spore_emphasis(segment.target)

        node.fields[field] = (
            segment.before + inline + segment.after
        )

        return node


    def apply_fragment_emphasis(
        self,
        node: Node,
        field: str,
        start: int,
        end: int,
        expected_text: Optional[str] = None
    ) -> Node:
        segment = self.get_content_portions(
            node.fields,
            field,
            start,
            end,
            expected_text
        )

        formatter = get_format(node.data.content_format)
        quoted = formatter.apply_fragment_emphasis(segment.target)

        before = ensure_double_newline_left(segment.before.rstrip())
        after = ensure_double_newline_right(segment.after.lstrip())

        node.fields[field] = before + quoted + after

        return node

    def remove_fragment_emphasis(
        self,
        node: Node,
        text: str,
        allowed_prefix_pattern: Optional[str] = None
    ) -> str:
        formatter = get_format(node.data.content_format)
        return formatter.remove_fragment_emphasis(text, allowed_prefix_pattern)
    
    def remove_spore_emphasis(self, node: Node, text: str) -> str:
        formatter = get_format(node.data.content_format)
        return formatter.remove_spore_emphasis(text)

    def remove_links(self, node: Node, field: str, start: int, end: int, expected_text: str) -> Node:
        segment = self.get_content_portions(node.fields, field, start, end, expected_text)
        
        formatter = get_format(node.data.content_format)
        cleaned = formatter.strip_links(segment.target)
        
        node.fields[field] = segment.before + cleaned + segment.after
        return node
