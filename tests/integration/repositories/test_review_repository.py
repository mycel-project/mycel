from src.models.node_state_before import NodeStateBefore, TYPE_DATA_MAP
from src.types.node_type import NodeType

def get_dummy_state(node_type: NodeType) -> NodeStateBefore:
    return NodeStateBefore(
        due=0,
        last_review=None,
        type_data=TYPE_DATA_MAP[node_type]()
    )

def test_review_create_and_delete(review_repo, app, create_user, create_col, generate_id):
    user, _ = create_user()
    col = create_col(user_id=user.id)
    node_id = generate_id()
    node_type = list(NodeType)[0]
    
    app.db.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due, content, data, type_data) VALUES (:id, :col_id, :type, 0, 0, 0, '{}', '{}', '{}')",
        {"id": node_id, "col_id": col.id, "type": node_type.value}
    )

    review = review_repo.create(
        node_id=node_id,
        type=node_type,
        node_state_before=get_dummy_state(node_type),
        duration=5000
    )

    assert review.id is not None
    assert review_repo.get_encounter_count(node_id) == 1

    review_repo.delete(review.id)
    assert review_repo.get_encounter_count(node_id) == 0

def test_review_node_queries(review_repo, app, create_user, create_col, generate_id):
    user, _ = create_user()
    col = create_col(user_id=user.id)
    node_type = list(NodeType)[0]
    
    node1_id = generate_id()
    node2_id = generate_id()

    app.db.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due, content, data, type_data) VALUES (:id, :col_id, :type, 0, 0, 0, '{}', '{}', '{}')",
        {"id": node1_id, "col_id": col.id, "type": node_type.value}
    )
    app.db.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due, content, data, type_data) VALUES (:id, :col_id, :type, 0, 0, 0, '{}', '{}', '{}')",
        {"id": node2_id, "col_id": col.id, "type": node_type.value}
    )

    for i in range(3):
        review_repo.create(node_id=node1_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=1000 + i)
        review_repo.create(node_id=node2_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=2000 + i)

    reviews_n1 = review_repo.get_by_node(node1_id)
    assert len(reviews_n1) == 3
    assert reviews_n1[0].time == 1000
    assert review_repo.get_encounter_count(node1_id) == 3

    reviews_n2 = review_repo.get_by_node(node2_id)
    assert len(reviews_n2) == 3
    assert reviews_n2[0].time == 2000
    assert review_repo.get_encounter_count(node2_id) == 3

def test_review_get_by_period(review_repo, app, create_user, create_col, generate_id):
    user, _ = create_user()
    col = create_col(user_id=user.id)
    node_id = generate_id()
    node_type = list(NodeType)[0]

    app.db.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due, content, data, type_data) VALUES (:id, :col_id, :type, 0, 0, 0, '{}', '{}', '{}')",
        {"id": node_id, "col_id": col.id, "type": node_type.value}
    )

    review_repo.create(node_id=node_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=100)
    review_repo.create(node_id=node_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=200)
    review_repo.create(node_id=node_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=300)

    results = review_repo.get_by_period(start=150, end=250, col_id=col.id)

    assert len(results) == 1
    assert results[0].time == 200

def test_review_get_last_by_collection(review_repo, app, create_user, create_col, generate_id):
    user, _ = create_user()
    col1 = create_col(user_id=user.id)
    node_type = list(NodeType)[0]
    
    node1_id = generate_id()
    app.db.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due, content, data, type_data) VALUES (:id, :col_id, :type, 0, 0, 0, '{}', '{}', '{}')",
        {"id": node1_id, "col_id": col1.id, "type": node_type.value}
    )
    review_repo.create(node_id=node1_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=1000)
    review_repo.create(node_id=node1_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=2000)
    
    col2 = create_col(user_id=user.id)
    node2_id = generate_id()

    app.db.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due, content, data, type_data) VALUES (:id, :col_id, :type, 0, 0, 0, '{}', '{}', '{}')",
        {"id": node2_id, "col_id": col2.id, "type": node_type.value}
    )
    review_repo.create(node_id=node2_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=3000)

    last_review = review_repo.get_last_review_by_collection(col1.id)
    
    assert last_review is not None
    assert last_review.time == 2000
    assert last_review.node_id == node1_id
