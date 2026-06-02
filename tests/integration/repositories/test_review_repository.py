from src.models.node_state_before import NodeStateBefore, TYPE_DATA_MAP
from src.repositories.review_repository import ReviewRepository
from src.types.node_type import NodeType

def get_dummy_state(node_type: NodeType) -> NodeStateBefore:
    return NodeStateBefore(
        due=0,
        last_review=None,
        type_data=TYPE_DATA_MAP[node_type]()
    )

def test_review_create_and_delete(db_fixture, default_node):
    repo = ReviewRepository(db=db_fixture)
    node_id, node_type = default_node
    
    review = repo.create(
        node_id=node_id,
        type=node_type,
        node_state_before=get_dummy_state(node_type),
        duration=5000
    )

    assert review.id is not None
    assert repo.get_encounter_count(node_id) == 1

    repo.delete(review.id)
    assert repo.get_encounter_count(node_id) == 0

def test_review_node_queries(db_fixture, default_collection, generate_id):
    repo = ReviewRepository(db=db_fixture)
    node_type = list(NodeType)[0]
    
    node1_id = generate_id()
    node2_id = generate_id()

    db_fixture.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due) VALUES (?, ?, ?, 0, 0, 0)", 
        (node1_id, default_collection, node_type.value)
    )
    db_fixture.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due) VALUES (?, ?, ?, 0, 0, 0)", 
        (node2_id, default_collection, node_type.value)
    )

    for i in range(3):
        repo.create(node_id=node1_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=1000 + i)
        repo.create(node_id=node2_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=2000 + i)

    reviews_n1 = repo.get_by_node(node1_id)
    assert len(reviews_n1) == 3
    assert reviews_n1[0].time == 1000
    assert repo.get_encounter_count(node1_id) == 3

    reviews_n2 = repo.get_by_node(node2_id)
    assert len(reviews_n2) == 3
    assert reviews_n2[0].time == 2000
    assert repo.get_encounter_count(node2_id) == 3

def test_review_get_by_period(db_fixture, default_node):
    repo = ReviewRepository(db=db_fixture)
    node_id, node_type = default_node

    repo.create(node_id=node_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=100)
    repo.create(node_id=node_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=200)
    repo.create(node_id=node_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=300)

    results = repo.get_by_period(start=150, end=250)
    
    assert len(results) == 1
    assert results[0].time == 200

def test_review_get_last_by_collection(db_fixture, default_collection, default_user, generate_id):
    repo = ReviewRepository(db=db_fixture)
    node_type = list(NodeType)[0]
    
    node1_id = generate_id()
    db_fixture.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due) VALUES (?, ?, ?, 0, 0, 0)", 
        (node1_id, default_collection, node_type.value)
    )

    repo.create(node_id=node1_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=1000)
    repo.create(node_id=node1_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=2000)

    col2_id = generate_id()
    node2_id = generate_id()
    
    db_fixture.execute(
        "INSERT INTO collections (id, user_id, name, created_at, updated_at) VALUES (?, ?, 'C2', 0, 0)", 
        (col2_id, default_user)
    )
    db_fixture.execute(
        "INSERT INTO nodes (id, collection_id, type, created_at, updated_at, due) VALUES (?, ?, ?, 0, 0, 0)", 
        (node2_id, col2_id, node_type.value)
    )
    
    repo.create(node_id=node2_id, type=node_type, node_state_before=get_dummy_state(node_type), duration=5000, now=3000)

    last_review = repo.get_last_review_by_collection(default_collection)
    
    assert last_review is not None
    assert last_review.time == 2000
    assert last_review.node_id == node1_id
