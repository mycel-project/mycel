import time
from uuid import uuid4

import pytest

from src.models.node import NodeType
from src.schemas.node_detail_view import NodeDetailView

class TestUser:
    def test_create_user(self, api):
        response = api.post("/users", body={"name": "test"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "test"

    def test_get_user_details(self, api, create_user):
        user, token = create_user()
        response = api.get(f"/users", token)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["data"]["created_at"], int)
        assert data["data"]["id"] == user.id

    def test_update_user(self, api, create_user):
        user, token = create_user()
        response = api.patch(f"/users", token, body={"name": "new name"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "new name"

    def test_export_user_data(self, api, create_user):
        user, token = create_user()
        response = api.get(f"/users/export", token)
        assert response.status_code == 200

    def test_import_user_data(self, api, create_user):
        user, token = create_user()
        response = api.post(f"/users/import", token, body={"payload": ""})
        assert response.status_code == 422
        
class TestCollection:
    def test_list_collections(self, api, create_user, create_col):
        user, token = create_user()
        col = create_col(user_id = user.id)

        response = api.get("/collections", token)

        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) >= 1

        assert data["data"][0]["name"] == col.name

    def test_create_collection(self, create_user, api):
        user, token = create_user()
        response = api.post("/collections", token, body={"name": "test"})    
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "test"

    def test_update_collection(self, api, create_user, create_col):
        user, token = create_user()
        col = create_col(user_id=user.id)
        response = api.patch(f"/collections/{col.id}", token, body={"name": "new name"})
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "new name"

    def test_delete_collection(self, api, create_user, create_col):
        user, token = create_user()
        col = create_col(user_id=user.id)
        response = api.delete(f"/collections/{col.id}", token)
        assert response.status_code == 204


class TestNode:
    def test_list_nodes(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        create_node(col_id=col.id, user_id=user.id)
        response = api.get(f"/collections/{col.id}/nodes", token)
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) >= 1

    def test_get_node(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        response = api.get(f"/collections/{col.id}/nodes/{node.id}", token)
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == node.id

    @pytest.mark.vcr 
    def test_create_node(self, api, create_user, create_col):
        user, token = create_user()
        col = create_col(user_id=user.id)
        response = api.post(f"/collections/{col.id}/nodes", token, body={"type": "url", "url": "https://example.com"})
        assert response.status_code == 200
        assert response.json()["data"]["collection_id"] == col.id

    def test_update_node(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        new_parent = create_node(col_id=col.id, user_id=user.id)
        response = api.patch(f"/collections/{col.id}/nodes/{node.id}", token, body={"parent_id": new_parent.id})
        data = response.json()["data"]
        assert isinstance(data, dict)
        assert response.status_code == 200
        assert response.json()["data"]["parent_id"] == new_parent.id
        
    def test_delete_node(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        response = api.delete(f"/collections/{col.id}/nodes/{node.id}", token)
        assert response.status_code == 200
        assert node.id in response.json()["data"]["deleted_ids"]

    def test_get_deleted_nodes(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        api.delete(f"/collections/{col.id}/nodes/{node.id}", token)
        response = api.get(f"/collections/{col.id}/nodes/deleted", token)
        assert response.status_code == 200
        deleted = response.json()["data"]
        assert any(n["id"] == node.id for n in deleted)

    def test_get_root_node(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        root = create_node(col_id=col.id, user_id=user.id)
        child = create_node(col_id=col.id, user_id=user.id, parent_id=root.id)
        response = api.get(f"/collections/{col.id}/nodes/{child.id}/root", token)
        assert response.status_code == 200
        assert response.json()["data"]["id"] == root.id

    def test_restore_node(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        api.delete(f"/collections/{col.id}/nodes/{node.id}", token)
        response = api.post(f"/collections/{col.id}/nodes/{node.id}/restore", token, body={})
        assert response.status_code == 200
        assert any(n["id"] == node.id for n in response.json()["data"])

    def test_get_outline(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        response = api.get(f"/collections/{col.id}/nodes/{node.id}/outline", token)
        assert response.status_code == 200
        assert "entries" in response.json()["data"]

    def test_create_extract(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, content="Hello world")
        response = api.post(
            f"/collections/{col.id}/nodes/{node.id}/extracts",
            token,
            body={
                "text": "Hello",
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
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, content="Hello world")
        response = api.post(
            f"/collections/{col.id}/nodes/{node.id}/remove-links",
            token,
            body={"text": "Hello", "start_index": 0, "end_index": 5}
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == node.id

    def test_split_node(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, content="# Title\n## Section")
        response = api.post(f"/collections/{col.id}/nodes/{node.id}/split", token, body={"level": 2, "tz_offset": 0})
        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)
        assert len(data) >= 1
        
class TestLearningUnit:
    def test_get_priorities(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node1 = create_node(col_id=col.id, user_id=user.id)
        time.sleep(0.01)
        node2 = create_node(col_id=col.id, user_id=user.id)
        response = api.get(f"/collections/{col.id}/nodes/priorities", token)
        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)
        node_ids = [item["node_id"] for item in data]
        assert str(node1.id) in node_ids
        assert str(node2.id) in node_ids
        
    def test_reprioritise_learning_unit(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        response = api.patch(f"/collections/{col.id}/nodes/{node.id}/slot/1/reprioritise", token, body={"priority": 0.5})
        assert response.status_code == 200
        assert response.json()["data"]["id"] == node.id

    def test_reschedule_learning_unit(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        response = api.patch(
            f"/collections/{col.id}/nodes/{node.id}/slot/1/reschedule/",
            token,
            body={"date": "2099-05-20", "tz_offset": 120}
        )
        assert response.status_code == 200
        assert response.json()["data"]["id"] == node.id

    def test_dismiss_fragment(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, content="Hello world")
        response = api.patch(
            f"/collections/{col.id}/nodes/{node.id}/slot/1/dismiss",
            token,
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == node.id
        assert data["learning_units"][0]["dismiss"] == True

    def test_dismiss_fragment_with_value(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, content="Hello world")
        response = api.patch(
            f"/collections/{col.id}/nodes/{node.id}/slot/1/dismiss",
            token,
            body={"value": False}
        )
        assert response.status_code == 200
        assert response.json()["data"]["learning_units"][0]["dismiss"] == False

    def test_update_spore_learning_data_partial(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id, content="content", type=NodeType.SPORE)

        initial = api.get(f"/collections/{col.id}/nodes/{node.id}", token).json()["data"]
        initial_lu = initial["learning_units"][0]
        initial_difficulty = initial_lu["learning_data"]["difficulty"]
        initial_due = initial_lu["due"]

        response = api.patch(
            f"/collections/{col.id}/nodes/{node.id}/slot/1",
            token,
            body={
                "type": "spore",
                "learning_data": {
                    "type": "fsrs",
                    "stability": 5.0
                }
            }
        )
        assert response.status_code == 200
        lu = response.json()["data"]["learning_units"][0]

        assert lu["learning_data"]["stability"] == 5.0
        assert lu["learning_data"]["difficulty"] == initial_difficulty
        assert lu["due"] == initial_due
        
class TestReview:
    def test_get_next_review(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        response = api.get(f"/collections/{col.id}/reviews/next", token)
        assert response.status_code == 200
        data = response.json()["data"]
        assert data is None or "id" in data

    def test_undo_review_no_pending(self, api, create_user, create_col):
        user, token = create_user()
        col = create_col(user_id=user.id)
        response = api.post(f"/collections/{col.id}/reviews/undo", token)
        assert response.status_code == 409

    def test_review_node_no_pending(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(col_id=col.id, user_id=user.id)
        response = api.post(
            f"/collections/{col.id}/nodes/{node.id}/review",
            token,
            body={"duration": 5000, "type_review_data": {"type": "spore", "rating": 3}, "tz_offset": 0}
        )
        assert response.status_code == 409
        
    def test_get_calendar(self, api, create_user, create_col):
        user, token = create_user()
        col = create_col(user_id=user.id)
        response = api.get(f"/collections/{col.id}/reviews/calendar", token)
        assert response.status_code == 200
        assert isinstance(response.json()["data"], list)

class TestIdempotency:
    def test_idempotent_post(self, api, create_user, create_col, create_node):
        user, token = create_user()
        col = create_col(user_id=user.id)
        node = create_node(user_id= user.id, col_id=col.id)
        key = str(uuid4())

        r1 = api.patch(
            f"/collections/{col.id}/nodes/{node.id}/slot/1/reschedule",
            token,
            body={"date": "2099-05-20", "tz_offset": 0},
            headers={"Idempotency-Key": key}
        )
        r2 = api.patch(
            f"/collections/{col.id}/nodes/{node.id}/slot/1/reschedule",
            token,
            body={"date": "2020-05-20", "tz_offset": 0},
            headers={"Idempotency-Key": key}
        ) # simulate incoherent request to make sure it reuse the first one

        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json() == r2.json()
