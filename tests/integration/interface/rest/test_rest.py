def test_list_collections(client, col, col_service):
    response = client.get("/collections")
    
    assert response.status_code == 200

    col = col_service.get_collection(col)

    data = response.json()
    assert "collections" in data
    assert len(data["collections"]) >= 1

    assert data["collections"][0]["name"] == col.name
