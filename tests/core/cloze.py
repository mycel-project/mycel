import pytest

from src.core.cloze import CLOZE_PATTERN, CLOZE_REGEX

REGEX = CLOZE_REGEX
PATTERN = CLOZE_PATTERN

@pytest.mark.parametrize("text, expected_groups", [
    ("{{c1::answer}}", ("answer", None)),
    ("{{c2::answer::hint}}", ("answer", "hint")),
    
    ("{{c10::answer}}", ("answer", None)),
    ("{{c99::answer::hint}}", ("answer", "hint")),
    
    ("{{c1::café}}", ("café", None)),
    ("{{c1::café:}}", ("café:", None)),
    ("{{c1::40%}}", ("40%", None)),
    ("{{c1::a+b}}", ("a+b", None)),
    ("{{c1::hello world}}", ("hello world", None)),
    ("{{c1::ligne1\nligne2}}", ("ligne1\nligne2", None)),
    ("{{c1::ligne1}test::yes}}", ("ligne1}test", "yes")),
    
    # Caractères spéciaux dans le hint
    ("{{c1::answer::hint with spaces}}", ("answer", "hint with spaces")),
    ("{{c1::answer::}}", ("answer", "")),  
    
    # Ne doit PAS matcher
    ("{{answer}}", None),
    ("{{c::answer}}", None),       
    ("c1::answer", None),          
    ("{c1::answer}", None),        
    ("{{c1::answer}", None),        
    ("{c1::answer:}}", None),        
])

def test_cloze_pattern(text, expected_groups):
    match = CLOZE_PATTERN.search(text)
    if expected_groups is None:
        assert match is None
    else:
        assert match is not None
        assert match.group(1) == expected_groups[0]
        assert match.group(2) == expected_groups[1]
