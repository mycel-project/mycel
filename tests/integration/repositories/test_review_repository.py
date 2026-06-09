import time
from src.models.fragment import Fragment
from src.models.learning_unit import LearningUnit
from src.models.node import NodeType
from src.models.spore import Spore
from src.models.type_review_data.fragment_review_data import FragmentReviewData
from src.models.type_review_data.spore_review_data import SporeReviewData


def get_dummy_state(node_type: NodeType) -> LearningUnit:
    if node_type == NodeType.FRAGMENT:
        return Fragment(node_id="", due=0)
    return Spore(node_id="", due=0)

def get_dummy_review_data(node_type: NodeType):
    if node_type == NodeType.FRAGMENT:
        return FragmentReviewData(type=NodeType.FRAGMENT.value)
    return SporeReviewData(type=NodeType.SPORE.value)

def test_review_create_and_delete(review_repo, create_user, create_col, create_node):
    user, _ = create_user()
    col = create_col(user_id=user.id)
    node_type = list(NodeType)[0]
    
    node = create_node(col_id=col.id, user_id=user.id, type=node_type)
    lu_id = node.learning_units[0].id

    review = review_repo.create(
        learning_unit_id=lu_id,
        type=node_type,
        state_before=get_dummy_state(node_type),
        type_review_data=get_dummy_review_data(node_type),
        duration=5000
    )

    assert review.id is not None
    assert review_repo.get_encounter_count(lu_id) == 1

    review_repo.delete(review.id)
    assert review_repo.get_encounter_count(lu_id) == 0

def test_review_node_queries(review_repo, app, create_user, create_col, create_node):
    user, _ = create_user()
    col = create_col(user_id=user.id)
    node_type = list(NodeType)[0]
    
    node1 = create_node(col_id=col.id, user_id=user.id, type=node_type)
    node2 = create_node(col_id=col.id, user_id=user.id, type=node_type)
    
    lu1_id = node1.learning_units[0].id
    lu2_id = node2.learning_units[0].id

    for i in range(3):
        review1 = review_repo.create(learning_unit_id=lu1_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
        app.db.execute("UPDATE reviews SET reviewed_at = :now WHERE id = :id", {"now": 1000 + i, "id": review1.id})
        
        review2 = review_repo.create(learning_unit_id=lu2_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
        app.db.execute("UPDATE reviews SET reviewed_at = :now WHERE id = :id", {"now": 2000 + i, "id": review2.id})

    reviews_n1 = review_repo.get_by_node(lu1_id)
    assert len(reviews_n1) == 3
    assert reviews_n1[0].reviewed_at == 1000
    assert review_repo.get_encounter_count(lu1_id) == 3

    reviews_n2 = review_repo.get_by_node(lu2_id)
    assert len(reviews_n2) == 3
    assert reviews_n2[0].reviewed_at == 2000
    assert review_repo.get_encounter_count(lu2_id) == 3

def test_review_get_by_period(review_repo, app, create_user, create_col, create_node):
    user, _ = create_user()
    col = create_col(user_id=user.id)
    node_type = list(NodeType)[0]

    node = create_node(col_id=col.id, user_id=user.id, type=node_type)
    lu_id = node.learning_units[0].id

    r1 = review_repo.create(learning_unit_id=lu_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
    app.db.execute("UPDATE reviews SET reviewed_at = 100 WHERE id = :id", {"id": r1.id})
    
    r2 = review_repo.create(learning_unit_id=lu_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
    app.db.execute("UPDATE reviews SET reviewed_at = 200 WHERE id = :id", {"id": r2.id})
    
    r3 = review_repo.create(learning_unit_id=lu_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
    app.db.execute("UPDATE reviews SET reviewed_at = 300 WHERE id = :id", {"id": r3.id})

    results = review_repo.get_by_period(start=150, end=250, col_id=col.id)

    assert len(results) == 1
    assert results[0].reviewed_at == 200

def test_review_get_last_by_collection(review_repo, app, create_user, create_col, create_node):
    user, _ = create_user()
    col1 = create_col(user_id=user.id)
    node_type = list(NodeType)[0]
    
    node1 = create_node(col_id=col1.id, user_id=user.id, type=node_type)
    lu1_id = node1.learning_units[0].id
    
    r1 = review_repo.create(learning_unit_id=lu1_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
    app.db.execute("UPDATE reviews SET reviewed_at = 1000 WHERE id = :id", {"id": r1.id})
    
    r2 = review_repo.create(learning_unit_id=lu1_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
    app.db.execute("UPDATE reviews SET reviewed_at = 2000 WHERE id = :id", {"id": r2.id})
    
    col2 = create_col(user_id=user.id)
    node2 = create_node(col_id=col2.id, user_id=user.id, type=node_type)
    lu2_id = node2.learning_units[0].id

    r3 = review_repo.create(learning_unit_id=lu2_id, type=node_type, state_before=get_dummy_state(node_type), type_review_data=get_dummy_review_data(node_type), duration=5000)
    app.db.execute("UPDATE reviews SET reviewed_at = 3000 WHERE id = :id", {"id": r3.id})

    last_review = review_repo.get_last_review_by_collection(col1.id)
    
    assert last_review is not None
    assert last_review.reviewed_at == 2000
    assert last_review.learning_unit_id == lu1_id
