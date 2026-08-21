import pytest
from src.domain.get_outline_usecase import GetOutlineUseCase

@pytest.fixture
def usecase():
    return GetOutlineUseCase()

def test_usecase_delegates_to_correct_format(usecase, make_node):
    node = make_node("# Title")
    
    result = usecase.execute(node)
    
    assert len(result.entries) == 1
    assert result.entries[0].title == "Title"
