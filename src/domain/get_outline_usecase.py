from src.formats.registry import get_format
from src.models.node import Node
from src.models.outline import Outline


class GetOutlineUseCase:
    def execute(self, node: Node) -> Outline:
        text = node.fields.get_content() or ""
        content_format = node.data.content_format
        formatter = get_format(content_format)
        return formatter.get_outline(text)
