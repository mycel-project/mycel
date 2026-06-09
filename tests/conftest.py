from unittest.mock import Mock
from fastapi.testclient import TestClient
from fractional_indexing import generate_n_keys_between
from src.db import Db
from pathlib import Path
import pytest
import os

import random
import time
from uuid import uuid4

from src.models import learning_unit
from src.models.fragment import Fragment
from src.models.node import Node, NodeFields, NodeType
from src.models.node_data import NodeData
from src.models.spore import Spore
from src.models.template import DefaultTemplate
from src.repositories.collection_repository import CollectionRepository
from src.repositories.node_repository import NodeRepository
from src.services.collection_service import CollectionService
from src.services.node_service import NodeService
from src.services.review_service import ReviewService

@pytest.fixture
def generate_id():
    def _make_id():
        return str(uuid4())
    return _make_id

@pytest.fixture
def db_fixture(tmp_path: Path):
    # for unit tests
    db_path = tmp_path / "test.db"
    db = Db(str(db_path))
    yield db 
    
    if db_path.exists():
        os.remove(db_path)

@pytest.fixture
def default_user(db_fixture: Db, generate_id):
    user_id = generate_id()
    db_fixture.execute(
        "INSERT INTO users (id, name, created_at, conf) VALUES (:id, 'default_user', 0, '{}')",
        {"id": user_id}
    )
    return user_id

@pytest.fixture
def default_collection(db_fixture, default_user, generate_id):
    col_id = generate_id()
    db_fixture.execute(
        "INSERT INTO collections (id, user_id, name, created_at, updated_at, conf, algoconf) VALUES (:id, :user_id, 'Test', 0, 0, '{}', '{}')",
        {"id": col_id, "user_id": default_user}
    )
    return col_id

@pytest.fixture
def default_node(db_fixture, default_collection, generate_id):
    node_id = generate_id()
    node_type = list(NodeType)[0]
    db_fixture.execute(
        "INSERT INTO nodes (id, collection_id, base_for, created_at, updated_at, due) VALUES (:id, :col_id, :type, 0, 0, 0)",
        {"id": node_id, "col_id": default_collection, "type": node_type.value}
    )
    return node_id, node_type

# default repos
@pytest.fixture
def node_repo(db_fixture):
    return NodeRepository(db_fixture)

@pytest.fixture
def col_repo(db_fixture):
    return CollectionRepository(db_fixture)

# default services

@pytest.fixture
def review_service():
    db = Mock()
    scheduling_engine = Mock()
    fsrs_service = Mock()
    node_service = Mock()
    pending_cache = Mock()
    
    repo = Mock()  
    
    service = ReviewService(
        db=db,
        scheduling_engine=scheduling_engine,
        fsrs_service=fsrs_service,
        node_service=node_service,
    )
    service._repo = repo
    
    return service

@pytest.fixture
def node_service():
    node_repo = Mock()
    learning_unit_repo = Mock()
    service = NodeService(node_repository=node_repo, learning_unit_repository=learning_unit_repo)
    service._node_repo = node_repo
    service._lu_repo = learning_unit_repo
    return service

@pytest.fixture
def col_service(col_repo):
    service = CollectionService(collection_repository=col_repo)
    return service

# FastAPI
@pytest.fixture
def client(app):
    return TestClient(app.interface.interface.app)



@pytest.fixture
def make_node(generate_id):
    def _make_node(text: str, type=NodeType.FRAGMENT) -> Node:
        if type == NodeType.FRAGMENT:
            learning_unit = Fragment(due=9999999999999)
            return Node(
                id=generate_id(),
                collection_id=generate_id(),
                base_for=NodeType.FRAGMENT,
                fields=NodeFields(root={"content": text}),
                created_at=0,
                updated_at=0,
                data=NodeData(),
                learning_units=[learning_unit],
                template_id=DefaultTemplate.FRAGMENT_BASIC
            )
        else:
            learning_unit = Spore(due=9999999999999)
            return Node(
                id=generate_id(),
                collection_id=generate_id(),
                base_for=NodeType.SPORE,
                fields=NodeFields(root={"cloze": text}),
                created_at=0,
                updated_at=0,
                data=NodeData(),
                learning_units=[learning_unit],
                template_id=DefaultTemplate.SPORE_CLOZE
            )
    return _make_node

# @pytest.fixture
# def nodes(db, col, default_user):
#     repo = NodeRepository(db)

#     now = int(time.time() * 1000)
#     day = 86_400_000

#     created = []

#     def create_fragment(i, **kwargs):
#         node = repo.create(
#             type=NodeType.FRAGMENT,
#             collection_id=col.id,
#             content=NodeContent.from_input({
#                 "0": (
#                     "Machine learning is a subfield of artificial intelligence that focuses on learning from data. "
#                     "It replaces explicit programming with statistical inference. "
#                     f"Example {i}: models can generalize from training data to unseen inputs."
#                 )
#             }),
#             data=None,
#             parent_id=kwargs.get("parent_id"),
#             priority=kwargs.get("priority"),
#         )
#         created.append(node)
#         return node

#     def create_spore(i, parent_id, **kwargs):
#         node = repo.create(
#             type=NodeType.SPORE,
#             collection_id=col.id,
#             content=NodeContent.from_input({
#                 "0": "Define {{c1::loss function}} and {{c1::gradient descent}}."
#             }),
#             data=None,
#             parent_id=parent_id,
#             priority=kwargs.get("priority"),
#         )
#         created.append(node)
#         return node

#     # generate valid fractional keys for fragments
#     fragment_keys = generate_n_keys_between(None, None, 20)

#     f1 = create_fragment(1, priority=fragment_keys[0])
#     f2 = create_fragment(2, priority=fragment_keys[1], parent_id=f1.id)
#     f3 = create_fragment(3, priority=fragment_keys[2], parent_id=f2.id)
#     f4 = create_fragment(4, priority=fragment_keys[3])
#     f5 = create_fragment(5, priority=fragment_keys[4])
#     f6 = create_fragment(6, priority=fragment_keys[5])
#     f7 = create_fragment(7, priority=fragment_keys[6])
#     f8 = create_fragment(8, priority=fragment_keys[7])
#     f9 = create_fragment(9, priority=fragment_keys[8])
#     f10 = create_fragment(10, priority=fragment_keys[9])


#     s1 = create_spore(1, f1.id, priority=fragment_keys[10])
#     s2 = create_spore(2, f2.id, priority=fragment_keys[11])
#     s3 = create_spore(3, f3.id, priority=fragment_keys[12])
#     s4 = create_spore(4, f4.id, priority=fragment_keys[13])
#     s5 = create_spore(5, f5.id, priority=fragment_keys[14])
#     s6 = create_spore(6, f6.id, priority=fragment_keys[15])
#     s7 = create_spore(7, f7.id, priority=fragment_keys[16])
#     s8 = create_spore(8, f8.id, priority=fragment_keys[17])

#     def rand_review(now_ts, due):
#         if random.random() < 0.2:
#             return None

#         return random.randint(
#             min(now_ts, due) - 10 * day,
#             min(now_ts, due),
#         )

#     updates = [
#         (f1, now - 12 * day),
#         (f2, now - 5 * day),
#         (f3, now - 1 * day),
#         (f4, now),
#         (f5, now + 2 * day),
#         (f6, now + 4 * day),
#         (f7, now + 6 * day),
#         (f8, now + 8 * day),
#         (f9, now + 10 * day),
#         (f10, now + 12 * day),

#         (s1, now - 3 * day),
#         (s2, now - 20 * day),
#         (s3, now - 1 * day),
#         (s4, now),
#         (s5, now + 1 * day),
#         (s6, now + 3 * day),
#         (s7, now + 5 * day),
#         (s8, now + 7 * day),
#     ]

#     for node, due in updates:
#         node.due = due
#         node.last_review = rand_review(now, due)

#         if node.type == NodeType.SPORE:
#             node.type_data.stability = 2.5
#             node.type_data.difficulty = 3.0

#         repo.update(node)

#     return repo.get_by_collection(default_user, col.id)


# @pytest.fixture
# def db_fixture(tmp_path):
#     test_db_url = os.getenv("TEST_DATABASE_URL")
#     
#     if test_db_url:
#         engine = create_engine(test_db_url)
#     else:
#         db_path = tmp_path / "test_db.sqlite"
#         engine = create_engine(
#             f"sqlite:///{db_path}",
#             connect_args={"check_same_thread": False}
#         )
#
#     Base.metadata.create_all(bind=engine)
#     TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
#     session = TestingSessionLocal()
#     
#     yield session
#     
#     session.close()
#     Base.metadata.drop_all(bind=engine)

# @pytest.fixture(autouse=True)
# def default_user(db_fixture) -> int:
#     from src.models.user_orm import UserORM
#     
#     user_id = 1
#     db_fixture.add(UserORM(id=user_id, name="default_user", created_at=0))
#     db_fixture.commit()
#         
#     return user_id
    
