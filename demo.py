"""
Standalone demo/test for the SRS engine.
Run with: python -m src.demo
"""
import json
import time

import fsrs

from src.db import Db
from src.models.card import Card
from src.repositories.collection_repository import CollectionRepository
from src.repositories.card_repository import CardRepository
from src.repositories.review_repository import ReviewRepository
from src.services.scheduler import review_card, get_due_cards, AGAIN, HARD, GOOD, EASY

RATING_LABELS = {
    fsrs.Rating.Again: "Again",
    fsrs.Rating.Hard:  "Hard",
    fsrs.Rating.Good:  "Good",
    fsrs.Rating.Easy:  "Easy",
}
STATE_LABELS = {1: "learning", 2: "review", 3: "relearning", 0: "new"}


def add_sample_card(collection_name: str, data: dict, tags: list | None = None) -> Card:
    db = Db()
    col_repo = CollectionRepository(db)
    existing = next((c for c in col_repo.list() if c.name == collection_name), None)
    col = existing or col_repo.create(collection_name)
    card = CardRepository(db).create(col.id, data, tags)
    print(f"[+] Card {card.id} in '{collection_name}'")
    print(f"    data: {json.dumps(card.data, ensure_ascii=False)}")
    return card


def simulate_review(card_id: int, rating: fsrs.Rating) -> None:
    db = Db()
    updated = review_card(db, card_id, rating)
    label = RATING_LABELS[rating]
    print(f"[review] card={card_id}  rating={label}")
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


def get_due(collection_id: int, now_ms: int | None = None) -> list[Card]:
    db = Db()
    cards = get_due_cards(db, collection_id, now_ms)
    label = "now" if now_ms is None else f"t+{(now_ms - int(time.time()*1000))//86400000}d"
    print(f"[due @ {label}] {len(cards)} card(s) in collection {collection_id}")
    for c in cards:
        print(f"  card={c.id}  state={STATE_LABELS.get(c.type, c.type)}  interval={c.interval}d")
    return cards


def print_card_state(card_id: int) -> None:
    db = Db()
    card = CardRepository(db).get(card_id)
    if not card:
        print(f"Card {card_id} not found")
        return
    reviews = ReviewRepository(db).get_by_card(card_id)
    print(f"\n── Card {card_id} ──────────────────────────────")
    print(f"  state:       {STATE_LABELS.get(card.type, card.type)}")
    print(f"  interval:    {card.interval} day(s)")
    print(f"  stability:   {card.stability}")
    print(f"  difficulty:  {card.difficulty}")
    print(f"  reps:        {card.reps}")
    print(f"  lapses:      {card.lapses}")
    print(f"  data:        {json.dumps(card.data, ensure_ascii=False)}")
    print(f"  tags:        {card.tags}")
    print(f"  reviews ({len(reviews)}):")
    for r in reviews:
        rating_label = RATING_LABELS.get(fsrs.Rating(r.rating), str(r.rating))
        print(f"    [{rating_label}] interval={r.interval}d")


if __name__ == "__main__":
    print("=== SRS Engine Demo (FSRS) ===\n")

    # 1. Add sample cards
    c1 = add_sample_card(
        "Python",
        {"type": "flashcard", "front": "What is a decorator?", "back": "A function that wraps another function."},
        tags=["python", "advanced"],
    )
    c2 = add_sample_card(
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

    # 4. Due cards in +30 days
    db = Db()
    col_id = CollectionRepository(db).list()[0].id
    future = int(time.time() * 1000) + 30 * 86_400_000
    get_due(col_id, now_ms=future)

    print()

    # 5. Final state
    print_card_state(c1.id)
    print_card_state(c2.id)
