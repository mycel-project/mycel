import pytest
from src.models.outline import Outline, OutlineEntry
from src.formats.markdown import MarkdownFormat

@pytest.fixture
def markdown_format():
    return MarkdownFormat()

def test_empty_content(markdown_format):
    result = markdown_format.get_outline("")
    assert result == Outline(entries=[])

def test_no_headings(markdown_format):
    result = markdown_format.get_outline("Just some text\nno headings here")
    assert result == Outline(entries=[])

def test_single_heading(markdown_format):
    result = markdown_format.get_outline("# Hello")
    assert result.entries == [OutlineEntry(level=1, title="Hello", offset=0)]

def test_space_before_heading(markdown_format):
    result = markdown_format.get_outline("    # Hello")
    assert result.entries == [OutlineEntry(level=1, title="Hello", offset=0)]

def test_multiple_headings(markdown_format):
    text = "# Title\n## Section\n### Subsection"
    result = markdown_format.get_outline(text)
    assert result.entries[0] == OutlineEntry(level=1, title="Title", offset=0)
    assert result.entries[1] == OutlineEntry(level=2, title="Section", offset=8)
    assert result.entries[2] == OutlineEntry(level=3, title="Subsection", offset=19)

def test_heading_levels(markdown_format):
    text = "\n".join(f"{'#' * i} H{i}" for i in range(1, 7))
    result = markdown_format.get_outline(text)
    assert len(result.entries) == 6
    for i, entry in enumerate(result.entries, 1):
        assert entry.level == i

def test_offset_accounts_for_newlines(markdown_format):
    text = "Some text\n# Heading"
    result = markdown_format.get_outline(text)
    assert result.entries[0].offset == len("Some text\n")

def test_blockquote_heading(markdown_format):
    result = markdown_format.get_outline("> # Hello")
    assert len(result.entries) == 1
    assert result.entries[0].level == 1
    assert result.entries[0].title == "Hello"

def test_blockquote_heading_with_space(markdown_format):
    result = markdown_format.get_outline(">  ## Section")
    assert len(result.entries) == 1
    assert result.entries[0].level == 2

def test_blockquote_heading_offset(markdown_format):
    text = "Some text\n> # Heading"
    result = markdown_format.get_outline(text)
    assert result.entries[0].offset == len("Some text\n")

def test_mixed_blockquote_and_normal_headings(markdown_format):
    text = "# Title\n> ## Quoted\n### Normal"
    result = markdown_format.get_outline(text)
    assert len(result.entries) == 3
    assert result.entries[0].level == 1
    assert result.entries[1].level == 2
    assert result.entries[2].level == 3
