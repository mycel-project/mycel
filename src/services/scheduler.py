import dataclasses
import time
from datetime import datetime, timezone
from typing import Optional

import fsrs

from src.db import Db
from src.models.node import Node
from src.models.review import Review
from src.repositories.node_repository import NodeRepository
from src.repositories.review_repository import ReviewRepository

# Re-export rating constants for convenience
AGAIN = fsrs.Rating.Again
HARD  = fsrs.Rating.Hard
GOOD  = fsrs.Rating.Good
EASY  = fsrs.Rating.Easy

_scheduler = fsrs.Scheduler()

def _to_fsrs_card(node: Node) -> fsrs.Card:
    state = fsrs.State(node.type) if node.type in (1, 2, 3) else fsrs.State.Learning
    due_dt = datetime.fromtimestamp(node.due / 1000, tz=timezone.utc)
    last_dt = (
        datetime.fromtimestamp(node.last_review / 1000, tz=timezone.utc)
        if node.last_review else None
    )
    return fsrs.Card(
        card_id=node.id,
        state=state,
        step=node.fsrs_step,
        stability=node.stability,
        difficulty=node.difficulty,
        due=due_dt,
        last_review=last_dt,
    )


def _apply_fsrs_result(node: Node, fsrs_card: fsrs.Card, rating: fsrs.Rating) -> Node:
    c = dataclasses.replace(node)
    c.type = fsrs_card.state.value
    c.queue = fsrs_card.state.value
    c.stability = fsrs_card.stability
    c.difficulty = fsrs_card.difficulty
    c.fsrs_step = fsrs_card.step
    c.due = int(fsrs_card.due.timestamp() * 1000)
    c.last_review = int(fsrs_card.last_review.timestamp() * 1000) if fsrs_card.last_review else None

    if fsrs_card.last_review:
        delta = fsrs_card.due - fsrs_card.last_review
        c.interval = max(0, delta.days)

    c.reps += 1
    if rating == fsrs.Rating.Again:
        c.lapses += 1

    return c


def review_node(db: Db, node_id: int, rating: fsrs.Rating) -> Node:
    nodes = NodeRepository(db)
    reviews = ReviewRepository(db)

    node = nodes.get(node_id)
    if not node:
        raise ValueError(f"Node {node_id} not found")

    state_before = fsrs.Card.to_dict(_to_fsrs_card(node))

    fsrs_card = _to_fsrs_card(node)
    updated_fsrs, _ = _scheduler.review_card(
        fsrs_card,
        rating,
        review_datetime=datetime.now(tz=timezone.utc),
    )

    updated = _apply_fsrs_result(node, updated_fsrs, rating)
    state_after = fsrs.Card.to_dict(_to_fsrs_card(updated))

    nodes.update(updated)

    reviews.create(Review(
        node_id=node_id,
        review_time=int(time.time() * 1000),
        rating=rating.value,
        review_type=node.type,
        interval=updated.interval,
        ease=updated.difficulty or 0.0,
        state_before=state_before,
        state_after=state_after,
    ))

    return updated


def get_due_nodes(db: Db, collection_id: int, now_ms: Optional[int] = None) -> list[Node]:
    return NodeRepository(db).get_due(collection_id, now_ms)
