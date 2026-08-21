import pytest
from unittest.mock import MagicMock, patch
from src.services.node_orchestrator import NodeOrchestrator
from src.models.node import NodeType

@pytest.fixture
def make_orchestrator():
    def _make():
        # Mocks
        node_service = MagicMock()
        fragment_service = MagicMock()
        spore_service = MagicMock()
        priority_service = MagicMock()
        ressource_service = MagicMock()
        node_view_builder = MagicMock()
        node_format_service = MagicMock()
        create_node_from_url_usecase = MagicMock()
        create_node_from_text_usecase = MagicMock()
        reschedule_usecase = MagicMock()
        reprioritise_usecase = MagicMock()
        get_outline_usecase = MagicMock()
        split_node_usecase = MagicMock()
        collection_service = MagicMock()
        
        orchestrator = NodeOrchestrator(
            node_service,
            fragment_service,
            spore_service,
            priority_service,
            ressource_service,
            node_view_builder,
            node_format_service,
            create_node_from_url_usecase,
            create_node_from_text_usecase,
            reschedule_usecase,
            reprioritise_usecase,
            get_outline_usecase,
            split_node_usecase,
            collection_service
        )
        
        class Mocks:
            pass
        m = Mocks()
        m.node_service = node_service
        m.fragment_service = fragment_service
        m.spore_service = spore_service
        m.split_node = split_node_usecase
        m.node_view_builder = node_view_builder
        
        return orchestrator, m
    return _make


class TestNodeOrchestratorAutoFormat:
    def test_split_node_applies_emphasis_if_auto_format_true(self, make_orchestrator):
        orchestrator, mocks = make_orchestrator()
        
        mock_node = MagicMock()
        mock_node.fields = {"content": "Some text"}
        mocks.node_service.get_node_for_user.return_value = mock_node
        mocks.split_node.execute.return_value = []
        
        orchestrator.split_node_to_detail_views(
            user_id="user_1", col_id="col_1", node_id="node_1", 
            field="content", auto_format=True, tz_offset_min=0, level=1
        )
        
        mocks.fragment_service.emphasize_region.assert_called_once_with(
            "node_1", NodeType.FRAGMENT, "content", 0, 9
        )

    def test_split_node_skips_emphasis_if_auto_format_false(self, make_orchestrator):
        orchestrator, mocks = make_orchestrator()
        
        mock_node = MagicMock()
        mock_node.fields = {"content": "Some text"}
        mocks.node_service.get_node_for_user.return_value = mock_node
        mocks.split_node.execute.return_value = []
        
        orchestrator.split_node_to_detail_views(
            user_id="user_1", col_id="col_1", node_id="node_1", 
            field="content", auto_format=False, tz_offset_min=0, level=1
        )
        
        mocks.fragment_service.emphasize_region.assert_not_called()

    @patch("src.services.node_orchestrator.ExtractResult")
    def test_create_extract_fragment_applies_emphasis_if_auto_format_true(self, mock_extract, make_orchestrator):
        orchestrator, mocks = make_orchestrator()
        
        mock_node = MagicMock()
        mock_node.base_for = NodeType.FRAGMENT
        mock_node.fields = {"content": "Hello World"}
        mocks.node_service.get_node_for_user.return_value = mock_node
        
        orchestrator.create_extract(
            user_id="user_1", col_id="col_1", extract_type=NodeType.FRAGMENT, 
            source_node_id="node_1", text="World", field="content", 
            start_index=6, end_index=11, auto_format=True, tz_offset_min=0
        )
        
        mocks.fragment_service.emphasize_region.assert_called_once_with(
            "node_1", NodeType.FRAGMENT, "content", 6, 11, "World"
        )

    @patch("src.services.node_orchestrator.ExtractResult")
    def test_create_extract_fragment_skips_emphasis_if_auto_format_false(self, mock_extract, make_orchestrator):
        orchestrator, mocks = make_orchestrator()
        
        mock_node = MagicMock()
        mock_node.base_for = NodeType.FRAGMENT
        mock_node.fields = {"content": "Hello World"}
        mocks.node_service.get_node_for_user.return_value = mock_node
        
        orchestrator.create_extract(
            user_id="user_1", col_id="col_1", extract_type=NodeType.FRAGMENT, 
            source_node_id="node_1", text="World", field="content", 
            start_index=6, end_index=11, auto_format=False, tz_offset_min=0
        )
        
        mocks.fragment_service.emphasize_region.assert_not_called()

    @patch("src.services.node_orchestrator.ExtractResult")
    def test_create_extract_spore_skips_emphasis_and_formatting_cleanup_if_auto_format_false(self, mock_extract, make_orchestrator):
        orchestrator, mocks = make_orchestrator()
        
        mock_node = MagicMock()
        mock_node.base_for = NodeType.FRAGMENT
        mock_node.fields = {"content": "Hello World"}
        mocks.node_service.get_node_for_user.return_value = mock_node
        
        mock_clozed_spore = MagicMock()
        mocks.spore_service.cloze_region.return_value = mock_clozed_spore
        
        orchestrator.create_extract(
            user_id="user_1", col_id="col_1", extract_type=NodeType.SPORE, 
            source_node_id="node_1", text="World", field="content", 
            start_index=6, end_index=11, auto_format=False, tz_offset_min=0
        )
        
        mocks.fragment_service.emphasize_region.assert_not_called()
        mocks.spore_service.remove_extract_formatting.assert_not_called()

    @patch("src.services.node_orchestrator.ExtractResult")
    def test_create_extract_spore_applies_emphasis_and_formatting_cleanup_if_auto_format_true(self, mock_extract, make_orchestrator):
        orchestrator, mocks = make_orchestrator()
        
        mock_node = MagicMock()
        mock_node.base_for = NodeType.FRAGMENT
        mock_node.fields = {"content": "Hello World"}
        mocks.node_service.get_node_for_user.return_value = mock_node
        
        mock_clozed_spore = MagicMock()
        mocks.spore_service.cloze_region.return_value = mock_clozed_spore
        
        orchestrator.create_extract(
            user_id="user_1", col_id="col_1", extract_type=NodeType.SPORE, 
            source_node_id="node_1", text="World", field="content", 
            start_index=6, end_index=11, auto_format=True, tz_offset_min=0
        )
        
        mocks.fragment_service.emphasize_region.assert_called_once()
        mocks.spore_service.remove_extract_formatting.assert_called_once()
