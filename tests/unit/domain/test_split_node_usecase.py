from unittest.mock import MagicMock
import pytest
from uuid import uuid4

from src.domain.domain_exceptions import NoHeadingToSplit
from src.domain.split_node_usecase import SplitNodeUseCase


@pytest.fixture
def generate_id():
    def _make_id():
        return str(uuid4())
    return _make_id


@pytest.fixture
def make_node(generate_id):
    def _make_node(node_id: str, text: str):
        from src.models.node import Node
        from src.models.node_content import NodeContent
        from src.models.node_data import NodeData
        from src.models.type_data.fragment_data import FragmentData
        from src.types.node_type import NodeType
        return Node(
            id=node_id,
            collection_id=generate_id(),
            type=NodeType.FRAGMENT,
            content=NodeContent(fields={"0": text}),
            created_at=0, updated_at=0, due=0,
            position="a",
            data=NodeData(),
            type_data=FragmentData(),
        )
    return _make_node


@pytest.fixture
def make_use_case(generate_id, make_node):
    def _make_use_case(node_text: str, node_id: str | None = None):
        if node_id is None:
            node_id = generate_id()
        node_service = MagicMock()
        node_service.get_node.return_value = make_node(node_id, node_text)

        create_fragment = MagicMock()
        create_fragment.execute = MagicMock(return_value=MagicMock())

        from src.domain.get_outline_usecase import GetOutlineUseCase
        get_outline = GetOutlineUseCase()

        uc = SplitNodeUseCase(node_service, create_fragment, get_outline)
        return uc, create_fragment.execute
    return _make_use_case


def get_content(cf, index: int) -> str:
    return cf.call_args_list[index][0][1]


class TestSplitNodeUseCase:

    def test_single_h1_no_intro_raises(self, generate_id, make_use_case):
        """Single heading with no intro = 1 fragment = should raise."""
        text = "# Title\nSome content under h1.\n"
        uc, cf = make_use_case(text)
        with pytest.raises(NoHeadingToSplit):
            uc.execute(generate_id(), generate_id(), 0, level=1)

    def test_intro_before_first_heading_is_captured(self, generate_id, make_use_case):
        text = "Intro paragraph.\n\n# Title\nContent.\n"
        uc, cf = make_use_case(text)
        results = uc.execute(generate_id(), generate_id(), 0, level=1)
        assert len(results) == 2
        assert "Intro paragraph." in get_content(cf, 0)

    def test_multiple_h1s_split_correctly(self, generate_id, make_use_case):
        text = "# First\nContent A.\n# Second\nContent B.\n# Third\nContent C.\n"
        uc, cf = make_use_case(text)
        results = uc.execute(generate_id(), generate_id(), 0, level=1)
        assert len(results) == 3
        contents = [get_content(cf, i) for i in range(len(cf.call_args_list))]
        assert any("# First" in c and "Content A." in c for c in contents)
        assert any("# Second" in c and "Content B." in c for c in contents)
        assert any("# Third" in c and "Content C." in c for c in contents)

    def test_level_1_ignores_h2_raises(self, generate_id, make_use_case):
        """Single H1 containing H2s = 1 fragment at level=1 = should raise."""
        text = "# Title\n## Sub\nContent.\n"
        uc, cf = make_use_case(text)
        with pytest.raises(NoHeadingToSplit):
            uc.execute(generate_id(), generate_id(), 0, level=1)

    def test_level_1_with_multiple_h1s_ignores_h2(self, generate_id, make_use_case):
        """Multiple H1s: H2s should be included in their parent H1 fragment."""
        text = "# Title A\n## Sub\nContent.\n# Title B\nMore.\n"
        uc, cf = make_use_case(text)
        results = uc.execute(generate_id(), generate_id(), 0, level=1)
        assert len(results) == 2
        contents = [get_content(cf, i) for i in range(len(cf.call_args_list))]
        assert any("## Sub" in c and "Content." in c for c in contents)

    def test_level_2_splits_on_h2(self, generate_id, make_use_case):
        text = "# Title\nIntro.\n## Sub A\nContent A.\n## Sub B\nContent B.\n"
        uc, cf = make_use_case(text)
        results = uc.execute(generate_id(), generate_id(), 0, level=2)
        assert len(results) == 3  # # Title+Intro, ## Sub A, ## Sub B
        contents = [get_content(cf, i) for i in range(len(cf.call_args_list))]
        assert any("## Sub A" in c for c in contents)
        assert any("## Sub B" in c for c in contents)

    def test_split_by_h1_when_only_h2_exist_raises(self, generate_id, make_use_case):
        """level=1 but only H2s → no entries → should raise."""
        text = "## Sub A\nContent A.\n## Sub B\nContent B.\n"
        uc, cf = make_use_case(text)
        with pytest.raises(NoHeadingToSplit):
            uc.execute(generate_id(), generate_id(), 0, level=1)

    def test_empty_content_raises(self, generate_id, make_use_case):
        text = ""
        uc, cf = make_use_case(text)
        with pytest.raises(NoHeadingToSplit):
            uc.execute(generate_id(), generate_id(), 0, level=3)

    def test_no_content_field_raises(self, generate_id):
        node_service = MagicMock()
        node = MagicMock()
        node.id = generate_id()
        node.content = None
        node_service.get_node.return_value = node

        from src.domain.get_outline_usecase import GetOutlineUseCase
        create_fragment = MagicMock()
        uc = SplitNodeUseCase(node_service, create_fragment, GetOutlineUseCase())
        with pytest.raises(NoHeadingToSplit):
            uc.execute(generate_id(), generate_id(), 0, level=2)

    def test_content_fully_preserved(self, generate_id, make_use_case):
        """All sections of the original text end up in fragments."""
        text = "Intro.\n# H1\nBody.\n## H2\nSub.\n"
        uc, cf = make_use_case(text)
        uc.execute(generate_id(), generate_id(), 0, level=2)
        combined = " ".join(get_content(cf, i) for i in range(len(cf.call_args_list)))
        for chunk in ["Intro.", "# H1", "Body.", "## H2", "Sub."]:
            assert chunk in combined

    def test_parent_id_passed_correctly(self, generate_id, make_use_case):
        text = "# A\nContent.\n# B\nMore.\n"
        parent_id = generate_id()
        uc, cf = make_use_case(text, node_id=parent_id)
        uc.execute(generate_id(), parent_id, 0, level=1)
        for c in cf.call_args_list:
            assert c[1]["parent_id"] == parent_id

    def test_tz_offset_passed_correctly(self, generate_id, make_use_case):
        text = "# A\nContent.\n# B\nMore.\n"
        uc, cf = make_use_case(text)
        uc.execute(generate_id(), generate_id(), tz_offset=120, level=1)
        for c in cf.call_args_list:
            assert c[1]["tz_offset"] == 120
