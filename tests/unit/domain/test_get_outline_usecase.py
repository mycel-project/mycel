import pytest
from src.models.outline import Outline, OutlineEntry
from src.domain.get_outline_usecase import GetOutlineUseCase


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
