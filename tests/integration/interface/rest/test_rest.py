class TestCollection:
    def test_list_collections(self, api, create_user, create_col):
        user = create_user()
        col = create_col(user_id = user.id)

        response = api.get("/collections")

        assert response.status_code == 200

        data = response.json()
        assert len(data["data"]) >= 1

        assert data["data"][0]["name"] == col.name

    def test_get_collection_details(self, api, create_user, create_col):
        user = create_user()
        col = create_col(user_id = user.id)

        response = api.get(f"/collections/{col.id}")

        data = response.json()
        assert isinstance(data["data"]["created_at"], int)

    def test_create_collection(self, create_user, api):
        create_user()
        response = api.post("/collections", body={"name": "test"})    
        assert response.status_code == 200
        assert response.json()["data"]["name"] == "test"
