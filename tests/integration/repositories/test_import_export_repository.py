def test_get_full_user_data(import_export_repo, create_user, create_col, create_node):
    user, token = create_user()
    col1 = create_col(user_id=user.id)
    col2 = create_col(user_id=user.id)

    for i in range(30):
        create_node(col_id=col1.id, user_id=user.id, content=f"content col1 {i}")

    for i in range(15):
        create_node(col_id=col2.id, user_id=user.id, content=f"content col2 {i}")

    data = import_export_repo.get_full_user_data(user.id)

    print(data)
    assert data["user"].id == user.id
    assert len(data["collections"]) == 2
    
    col_ids = [c.id for c in data["collections"]]
    assert col1.id in col_ids
    assert col2.id in col_ids

    assert len(data["nodes"]) == 45
    assert len([n for n in data["nodes"] if n.collection_id == col1.id]) == 30
    assert len([n for n in data["nodes"] if n.collection_id == col2.id]) == 15
    
    assert len(data["reviews"]) == 0
