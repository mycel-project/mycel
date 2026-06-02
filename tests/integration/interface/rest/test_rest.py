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

