from src.models.node_create import NodeCreateFromText
from src.models.node_data import NodeSource

class TestCreateNodeFromTextUseCase:
    def test_without_title_and_source(self, create_user, create_col, node_repo, create_node_from_text_use_case):
        user, _ = create_user()
        col = create_col(user_id=user.id)

        content = "Test content"
        data = NodeCreateFromText(
            type="text",
            content=content,
        )
        node = create_node_from_text_use_case.execute(user.id, col.id, data)
        
        saved_node = node_repo.get(node.id)
    
        assert saved_node is not None
        assert saved_node.collection_id == col.id
        assert saved_node.fields.root["content"] == content
        assert saved_node.data.title == None
        assert saved_node.data.source == None

    def test_with_title_and_source(self, create_user, create_col, node_repo, create_node_from_text_use_case):
        user, _ = create_user()
        col = create_col(user_id=user.id)

        content = "Test content"
        title = "Test title"
        source = "Test source"
        data = NodeCreateFromText(
            type="text",
            content=content,
            title=title,
            source=NodeSource(path=source),
        )
        node = create_node_from_text_use_case.execute(user.id, col.id, data)
        
        saved_node = node_repo.get(node.id)
    
        assert saved_node is not None
        assert saved_node.collection_id == col.id
        assert saved_node.fields.root["content"] == content
        assert saved_node.data.title == title
        assert saved_node.data.source.path == source
