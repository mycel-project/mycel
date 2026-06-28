from pathlib import Path
import time
import random

from src.db import Db
from src.models.node_content import NodeContent
from src.repositories.node_repository import NodeRepository
from src.services.collection_service import CollectionService
from src.types.node_type import NodeType
from fractional_indexing import generate_n_keys_between


def main():
    db_path = Path("db_test.db")

    if db_path.exists():
        db_path.unlink()

    from src.core.config import build_db_url
    db = Db(build_db_url(str(db_path)))

    collection_service = CollectionService(db)
    repo = NodeRepository(db)

    col = collection_service.create_collection("pytest", 1)

    now = int(time.time() * 1000)
    day = 86_400_000

    created = []

    def create_fragment(i, **kwargs):
        node = repo.create(
            type=NodeType.FRAGMENT,
            collection_id=col.id,
            content=NodeContent.from_input({
                "0": (
                    "Machine learning is a subfield of artificial intelligence that focuses on learning from data. "
                    "It replaces explicit programming with statistical inference. "
                    f"Example {i}: models can generalize from training data to unseen inputs."
                )
            }),
            data=None,
            parent_id=kwargs.get("parent_id"),
            position=kwargs.get("position"),
        )
        created.append(node)
        return node

    def create_spore(i, parent_id, **kwargs):
        node = repo.create(
            type=NodeType.SPORE,
            collection_id=col.id,
            content=NodeContent.from_input({
                "0": "Define "+str(i)+" {{c1::loss function}} and {{c1::gradient descent}}."
            }),
            data=None,
            parent_id=parent_id,
            position=kwargs.get("position"),
        )
        created.append(node)
        return node

    # generate valid fractional keys for fragments
    fragment_keys = generate_n_keys_between(None, None, 20)

    f1 = create_fragment(1, position=fragment_keys[0])
    f2 = create_fragment(2, position=fragment_keys[1], parent_id=f1.id)
    f3 = create_fragment(3, position=fragment_keys[2], parent_id=f2.id)
    f4 = create_fragment(4, position=fragment_keys[3])
    f5 = create_fragment(5, position=fragment_keys[4])
    f6 = create_fragment(6, position=fragment_keys[5])
    f7 = create_fragment(7, position=fragment_keys[6])
    f8 = create_fragment(8, position=fragment_keys[7])
    f9 = create_fragment(9, position=fragment_keys[8])
    f10 = create_fragment(10, position=fragment_keys[9])


    s1 = create_spore(1, f1.id, position=fragment_keys[10])
    s2 = create_spore(2, f2.id, position=fragment_keys[11])
    s3 = create_spore(3, f3.id, position=fragment_keys[12])
    s4 = create_spore(4, f4.id, position=fragment_keys[13])
    s5 = create_spore(5, f5.id, position=fragment_keys[14])
    s6 = create_spore(6, f6.id, position=fragment_keys[15])
    s7 = create_spore(7, f7.id, position=fragment_keys[16])
    s8 = create_spore(8, f8.id, position=fragment_keys[17])

    def rand_review(now_ts, due):
        if random.random() < 0.2:
            return None

        return random.randint(
            min(now_ts, due) - 10 * day,
            min(now_ts, due),
        )

    updates = [
        (f1, now - 12 * day),
        (f2, now - 5 * day),
        (f3, now - 1 * day),
        (f4, 1779145200000),
        (f5, now + 2 * day),
        (f6, now + 4 * day),
        (f7, now + 6 * day),
        (f8, now + 8 * day),
        (f9, now + 10 * day),
        (f10, now + 12 * day),

        (s1, now - 3 * day),
        (s2, now - 20 * day),
        (s3, now - 1 * day),
        (s4, 1779224400000),
        (s5, now + 1 * day),
        (s6, now + 3 * day),
        (s7, now + 5 * day),
        (s8, now + 7 * day),
    ]

    for node, due in updates:
        node.due = due
        node.last_review = rand_review(now, due)

        if node.type == NodeType.SPORE:
            node.type_data.stability = 2.5
            node.type_data.difficulty = 3.0

        repo.update(node)

    print(f"✅ Test DB created at {db_path}")
    print(f"📦 Collection id: {col.id}")
    print(f"📊 Nodes: {len(created)}")


if __name__ == "__main__":
    main()
