"""
Standalone demo/test for the SRS engine.
Run with: python -m src.demo
"""
import json
import time

import fsrs

from src.db import Db
from src.models.node import Node
from src.repositories.collection_repository import CollectionRepository
from src.repositories.node_repository import NodeRepository
from src.repositories.review_repository import ReviewRepository
from src.services.scheduler import review_node, get_due_nodes, AGAIN, HARD, GOOD, EASY

RATING_LABELS = {
    fsrs.Rating.Again: "Again",
    fsrs.Rating.Hard:  "Hard",
    fsrs.Rating.Good:  "Good",
    fsrs.Rating.Easy:  "Easy",
}
STATE_LABELS = {1: "learning", 2: "review", 3: "relearning", 0: "new"}


def add_sample_node(collection_name: str, data: dict, tags: list | None = None) -> Node:
    db = Db()
    col_repo = CollectionRepository(db)
    existing = next((c for c in col_repo.list() if c.name == collection_name), None)
    col = existing or col_repo.create(collection_name)
    node = NodeRepository(db).create(col.id, data, tags)
    print(f"[+] Node {node.id} in '{collection_name}'")
    print(f"    data: {json.dumps(node.data, ensure_ascii=False)}")
    return node


def simulate_review(node_id: int, rating: fsrs.Rating) -> None:
    db = Db()
    updated = review_node(db, node_id, rating)
    label = RATING_LABELS[rating]
    print(f"[review] node={node_id}  rating={label}")
    print(f"  → state={STATE_LABELS.get(updated.type, updated.type)}"
          f"  interval={updated.interval}d"
          f"  stability={updated.stability:.4f}" if updated.stability else
          f"  → state={STATE_LABELS.get(updated.type, updated.type)}"
          f"  interval={updated.interval}d"
          f"  stability=None"
          )
    print(f"     difficulty={updated.difficulty:.4f}  reps={updated.reps}  lapses={updated.lapses}"
          if updated.difficulty else
          f"     difficulty=None  reps={updated.reps}  lapses={updated.lapses}")


def get_due(collection_id: int, now_ms: int | None = None) -> list[Node]:
    db = Db()
    nodes = get_due_nodes(db, collection_id, now_ms)
    label = "now" if now_ms is None else f"t+{(now_ms - int(time.time()*1000))//86400000}d"
    print(f"[due @ {label}] {len(nodes)} node(s) in collection {collection_id}")
    for c in nodes:
        print(f"  node={c.id}  state={STATE_LABELS.get(c.type, c.type)}  interval={c.interval}d")
    return nodes


def print_node_state(node_id: int) -> None:
    db = Db()
    node = NodeRepository(db).get(node_id)
    if not node:
        print(f"Node {node_id} not found")
        return
    reviews = ReviewRepository(db).get_by_node(node_id)
    print(f"\n── Node {node_id} ──────────────────────────────")
    print(f"  state:       {STATE_LABELS.get(node.type, node.type)}")
    print(f"  interval:    {node.interval} day(s)")
    print(f"  stability:   {node.stability}")
    print(f"  difficulty:  {node.difficulty}")
    print(f"  reps:        {node.reps}")
    print(f"  lapses:      {node.lapses}")
    print(f"  data:        {json.dumps(node.data, ensure_ascii=False)}")
    print(f"  tags:        {node.tags}")
    print(f"  reviews ({len(reviews)}):")
    for r in reviews:
        rating_label = RATING_LABELS.get(fsrs.Rating(r.rating), str(r.rating))
        print(f"    [{rating_label}] interval={r.interval}d")


if __name__ == "__main__":
    print("=== SRS Engine Demo (FSRS) ===\n")

    # 1. Add sample nodes
    c1 = add_sample_node(
        "Python",
        {"type": "flashnode", "front": "What is a decorator?", "back": "A function that wraps another function."},
        tags=["python", "advanced"],
    )
    c2 = add_sample_node(
        "Python",
        {"type": "article", "title": "PEP 572 – Assignment Expressions", "url": "https://peps.python.org/pep-0572/"},
        tags=["pep", "python"],
    )

    print()

    # 2. First review cycle
    simulate_review(c1.id, GOOD)
    simulate_review(c2.id, AGAIN)

    print()

    # 3. Second review cycle
    simulate_review(c1.id, EASY)
    simulate_review(c2.id, GOOD)

    print()

    # 4. Due nodes in +30 days
    db = Db()
    col_id = CollectionRepository(db).list()[0].id
    future = int(time.time() * 1000) + 30 * 86_400_000
    get_due(col_id, now_ms=future)

    print()

    # 5. Final state
    print_node_state(c1.id)
    print_node_state(c2.id)
