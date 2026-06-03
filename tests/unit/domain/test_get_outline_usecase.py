import pytest
from src.models.node import Node
from src.models.node_content import NodeContent
from src.models.node_data import NodeData
from src.models.outline import Outline, OutlineEntry
from src.domain.get_outline_usecase import GetOutlineUseCase
from src.models.type_data.fragment_data import FragmentData
from src.types.node_type import NodeType

@pytest.fixture
def make_node(generate_id):
    def _make_node(text: str) -> Node:
        return Node(
            id=generate_id(),
            collection_id=generate_id(),
            type=NodeType.FRAGMENT,
            content=NodeContent(fields={"0": text}),
            created_at=0,
            updated_at=0,
            due=0,
            position="a",
            data=NodeData(),
            type_data=FragmentData(),
        )
    return _make_node

@pytest.fixture
def usecase():
    return GetOutlineUseCase()

def test_empty_content(usecase, make_node):
    node = make_node("")
    result = usecase.execute(node)
    assert result == Outline(entries=[])

def test_no_headings(usecase, make_node):
    node = make_node("Just some text\nno headings here")
    result = usecase.execute(node)
    assert result == Outline(entries=[])

def test_single_heading(usecase, make_node):
    node = make_node("# Hello")
    print(node)
    result = usecase.execute(node)
    assert result.entries == [OutlineEntry(level=1, title="Hello", offset=0)]
    
def test_space_before_heading(usecase, make_node):
    node = make_node("    # Hello")
    print(node)
    result = usecase.execute(node)
    assert result.entries == [OutlineEntry(level=1, title="Hello", offset=0)]
    
def test_multiple_headings(usecase, make_node):
    text = "# Title\n## Section\n### Subsection"
    node = make_node(text)
    result = usecase.execute(node)
    assert result.entries[0] == OutlineEntry(level=1, title="Title", offset=0)
    assert result.entries[1] == OutlineEntry(level=2, title="Section", offset=8)
    assert result.entries[2] == OutlineEntry(level=3, title="Subsection", offset=19)

def test_heading_levels(usecase, make_node):
    text = "\n".join(f"{'#' * i} H{i}" for i in range(1, 7))
    node = make_node(text)
    result = usecase.execute(node)
    assert len(result.entries) == 6
    for i, entry in enumerate(result.entries, 1):
        assert entry.level == i
        
def test_offset_accounts_for_newlines(usecase, make_node):
    text = "Some text\n# Heading"
    node = make_node(text)
    result = usecase.execute(node)
    assert result.entries[0].offset == len("Some text\n")

def test_blockquote_heading(usecase, make_node):
    node = make_node("> # Hello")
    result = usecase.execute(node)
    assert len(result.entries) == 1
    assert result.entries[0].level == 1
    assert result.entries[0].title == "Hello"

def test_blockquote_heading_with_space(usecase, make_node):
    node = make_node(">  ## Section")
    result = usecase.execute(node)
    assert len(result.entries) == 1
    assert result.entries[0].level == 2

def test_blockquote_heading_offset(usecase, make_node):
    text = "Some text\n> # Heading"
    node = make_node(text)
    result = usecase.execute(node)
    assert result.entries[0].offset == len("Some text\n")

def test_mixed_blockquote_and_normal_headings(usecase, make_node):
    text = "# Title\n> ## Quoted\n### Normal"
    node = make_node(text)
    result = usecase.execute(node)
    assert len(result.entries) == 3
    assert result.entries[0].level == 1
    assert result.entries[1].level == 2
    assert result.entries[2].level == 3
