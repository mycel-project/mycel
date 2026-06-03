import time

from src.types.node_type import NodeType

class TestUser:
    def test_create_user(self, api):
        response = api.post("/users", body={"name": "test"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "test"

    def test_get_user_details(self, api, create_user):
        user = create_user()
        response = api.get(f"/users/{user.id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"]["created_at"], int)
        assert data["data"]["id"] == user.id

    def test_update_user(self, api, create_user):
        user = create_user()
        response = api.patch(f"/users/{user.id}", body={"name": "new name"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "new name"

        
class TestCollection:
    def test_list_collections(self, api, create_user, create_col):
        user = create_user()
        col = create_col(user_id = user.id)

        response = api.get("/collections")

        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) >= 1

        assert data["data"][0]["name"] == col.name

    def test_create_collection(self, create_user, api):
        create_user()
        response = api.post("/collections", body={"name": "test"})    
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "test"

    def test_update_collection(self, api, create_user, create_col):
        user = create_user()
        col = create_col(user_id=user.id)
        response = api.patch(f"/collections/{col.id}", body={"name": "new name"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "new name"

    def test_delete_collection(self, api, create_user, create_col):
        user = create_user()
        col = create_col(user_id=user.id)
        response = api.delete(f"/collections/{col.id}")
        assert response.status_code == 204


class TestNode:
    def test_list_nodes(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        create_node(col_id=col.id)
        response = api.get(f"/collections/{col.id}/nodes")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1

    def test_get_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        response = api.get(f"/collections/{col.id}/nodes/{node.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == node.id

    def test_create_node(self, api, create_user, create_col):
        user = create_user()
        col = create_col(user_id=user.id)
        response = api.post(f"/collections/{col.id}/nodes", body={"type": "url", "url": "https://example.com"})
        assert response.status_code == 200
        assert response.json()["data"]["collection_id"] == col.id

    def test_update_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        response = api.patch(f"/collections/{col.id}/nodes/{node.id}", body={"due": 9999999999})
        assert response.status_code == 200
        assert response.json()["data"]["due"] == 9999999999
        
    def test_delete_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        response = api.delete(f"/collections/{col.id}/nodes/{node.id}")
        assert response.status_code == 200
        assert node.id in response.json()["data"]["deleted_ids"]
        
    def test_get_priorities(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node1 = create_node(col_id=col.id)
        time.sleep(0.01)
        node2 = create_node(col_id=col.id)
        response = api.get(f"/collections/{col.id}/nodes/priorities")
        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, dict)
        assert str(node1.id) in data
        assert str(node2.id) in data

    def test_get_deleted_nodes(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        api.delete(f"/collections/{col.id}/nodes/{node.id}")
        response = api.get(f"/collections/{col.id}/nodes/deleted")
        assert response.status_code == 200
        deleted = response.json()["data"]
        assert any(n["id"] == node.id for n in deleted)

    def test_get_root_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        root = create_node(col_id=col.id)
        child = create_node(col_id=col.id, parent_id=root.id)
        response = api.get(f"/collections/{col.id}/nodes/{child.id}/root")
        assert response.status_code == 200
        assert response.json()["data"]["id"] == root.id

    def test_reschedule_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        response = api.post(
            f"/collections/{col.id}/nodes/{node.id}/reschedule",
            body={"date": "2099-05-20", "tz_offset": 120}
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == node.id

    def test_restore_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        api.delete(f"/collections/{col.id}/nodes/{node.id}")
        response = api.post(f"/collections/{col.id}/nodes/{node.id}/restore", body={})
        assert response.status_code == 200
        assert any(n["id"] == node.id for n in response.json()["data"])

    def test_reprioritise_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        response = api.post(f"/collections/{col.id}/nodes/{node.id}/reprioritise", body={"priority": 0.5})
        assert response.status_code == 200
        assert response.json()["data"]["id"] == node.id

    def test_get_outline(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id)
        response = api.get(f"/collections/{col.id}/nodes/{node.id}/outline")
        assert response.status_code == 200
        assert "entries" in response.json()["data"]

    def test_create_extract(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, content="Hello world")
        response = api.post(
            f"/collections/{col.id}/nodes/{node.id}/extracts",
            body={
                "text": "Hello",
                "field": 0,
                "start_index": 0,
                "end_index": 5,
                "extract_type": NodeType.FRAGMENT,
                "tz_offset": 0,
            }
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert "extract_node" in data
        assert "source_node" in data

    def test_remove_links(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, content="Hello world")
        response = api.post(
            f"/collections/{col.id}/nodes/{node.id}/remove-links",
            body={"text": "Hello", "field": 0, "start_index": 0, "end_index": 5}
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == node.id

    def test_split_node(self, api, create_user, create_col, create_node):
        user = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, content="# Title\n## Section")
        response = api.post(f"/collections/{col.id}/nodes/{node.id}/split", body={"level": 1, "tz_offset": 0})
        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1
