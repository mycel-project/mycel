import time
from src.models.node import NodeFields, NodeType

class TestNodeRepositoryBasic:
    def test_create_and_get(self, node_repo, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        created = node_repo.create(
            collection_id=col.id,
            template_id="01",
            base_for=NodeType.SPORE,
            fields=NodeFields.from_dict({"content": ""})
        )
        assert created.id is not None
        
        fetched = node_repo.get(created.id)
        assert fetched is not None
        assert fetched.id == created.id
        assert fetched.template_id == "01"
        assert fetched.base_for == NodeType.SPORE

    def test_update(self, node_repo, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node = node_repo.create(col.id, "01", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}))
        node.template_id = "02"
        
        node_repo.update(node)
        
        updated = node_repo.get(node.id)
        assert updated.template_id == "02"

    def test_delete(self, node_repo, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node = node_repo.create(col.id, "01", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}))
        node_repo.delete(node.id)
        assert node_repo.get(node.id) is None

class TestNodeRepositoryQueries:
    def test_get_by_collection(self, node_repo, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node_repo.create(col.id, "01", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}))
        node_repo.create(col.id, "02", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}))
        
        results = node_repo.get_by_collection(col.id)
        assert len(results) == 2
        assert results[0].template_id == "01"

        limited = node_repo.get_by_collection(col.id, limit=1)
        assert len(limited) == 1

    def test_get_by_type(self, node_repo, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node_repo.create(col.id, "01", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}))
        node_repo.create(col.id, "02", NodeType.FRAGMENT, NodeFields.from_dict({"content": ""}))
        
        spores = node_repo.get_by_type(col.id, NodeType.SPORE.value)
        assert len(spores) == 1
        assert spores[0].base_for == NodeType.SPORE

    def test_hierarchy(self, node_repo, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        parent = node_repo.create(col.id, "01", NodeType.FRAGMENT, NodeFields.from_dict({"content": ""}))
        child1 = node_repo.create(col.id, "02", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}), parent_id=parent.id)
        child2 = node_repo.create(col.id, "03", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}), parent_id=child1.id)

        direct_children = node_repo.get_children(parent.id)
        assert len(direct_children) == 1
        assert direct_children[0].id == child1.id

        all_descendants = node_repo.get_children_recursive(parent.id)
        assert len(all_descendants) == 2

    def test_expired_deleted(self, node_repo, create_user, create_col):
        user, _ = create_user()
        col = create_col(user_id=user.id)
        
        node = node_repo.create(col.id, "01", NodeType.SPORE, NodeFields.from_dict({"cloze": ""}))
        node.deleted_at = 1000
        node_repo.update(node)

        expired = node_repo.get_expired_deleted(col.id, cutoff_ms=2000)
        assert len(expired) == 1

        not_expired = node_repo.get_expired_deleted(col.id, cutoff_ms=500)
        assert len(not_expired) == 0
