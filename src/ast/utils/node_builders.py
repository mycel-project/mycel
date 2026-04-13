from src.ast.nodes import Element, Text, Root
from src.ast.contracts import Properties

def create_element(
    tag: str,
    children: list | None = None,
    properties: Properties | None = None,
) -> Element:
    return Element(
        tagName=tag,
        properties=properties or {},
        children=children or [],
    )

def create_text(value: str) -> Text:
    return Text(value=value)

def create_root(children: list | None = None) -> Root:
    return Root(children=children or [])
