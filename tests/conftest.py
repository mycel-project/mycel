from src.db import Db
from pathlib import Path
import pytest

from src.models.node_content import NodeContent
from src.repositories.node_repository import NodeRepository
from src.services.collection_service import CollectionService

@pytest.fixture
def db():
    return Db(Path("file::memory:?cache=shared"))

@pytest.fixture
def col(db):
    service = CollectionService(db)

    col = service.create_collection("test")

    return col  

@pytest.fixture
def nodes(db, col):
    import time
    import random

    repo = NodeRepository(db)

    now = int(time.time() * 1000)
    day = 86_400_000
    hour = 3_600_000

    created = []

    def create_node(i, **kwargs):
        node = repo.create(
            collection_id=col.id,
            content=NodeContent.from_input({
                "text": f"learning concept {i}"
            }),
            data=None,
            parent_id=kwargs.get("parent_id"),
            priority=kwargs.get("priority"),
        )
        created.append(node)
        return node

    n1 = create_node(1, priority="Aa")
    n2 = create_node(2, priority="Ab")
    n3 = create_node(3, priority="Ac")

    n4 = create_node(4, parent_id=n3.id, priority="Aaa")
    n5 = create_node(5, parent_id=n4.id, priority="Aab")
    n6 = create_node(6, parent_id=n5.id, priority="A")

    n7 = create_node(7, priority="Ma")
    n8 = create_node(8, parent_id=n7.id, priority="Zz")
    n9 = create_node(9, parent_id=n7.id, priority="Cbc")

    n10 = create_node(10, priority="Bef")
    n11 = create_node(11, parent_id=n10.id, priority="Mas")

    n12 = create_node(12, priority="Ba")
    n13 = create_node(13, priority="Zccd")
    n14 = create_node(14, priority="Zqs")
    n15 = create_node(15, priority="Zv")

    def rand_hours():
        return random.randint(-6, 6) * hour

    updates = [
        (n1, now - 10 * day),
        (n2, now - 2 * day),
        (n3, now),

        (n4, now + 1 * day),
        (n5, now + 3 * day),
        (n6, now + 7 * day),

        (n7, now - 1 * day),
        (n8, now - 15 * day),
        (n9, now + 20 * day),

        (n10, now - 25 * day),
        (n11, now + 30 * day),

        (n12, now - 40 * day),
        (n13, now + 50 * day),
        (n14, now - 60 * day),
        (n15, now + 90 * day),
    ]

    for node, due in updates:
        node.due = due

        # règle importante :
        # last_review doit être <= due
        max_review = min(now, due)
        min_review = max_review - 10 * day

        node.last_review = random.randint(min_review, max_review)

        node.stability = 2.5
        node.difficulty = 3.0

        repo.update(node)

    return repo.get_by_collection(col.id)
