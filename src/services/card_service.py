from typing import Optional

from src.db import Db
from src.models.card import Card
from src.repositories.card_repository import CardRepository
from src.services.ordering_service import insert_between


class CardService:
    def __init__(self, db: Db):
        self._repo = CardRepository(db)

    def _resolve_position(
        self,
        collection_id: int,
        before_id: int | None,
        after_id: int | None,
    ) -> str:
        if before_id is None and after_id is None:
            return insert_between(self._repo.get_tail_key(collection_id), None)
        a_key, b_key = self._repo.get_neighbor_keys(collection_id, before_id, after_id)
        return insert_between(a_key, b_key)

    def create_card(
        self,
        collection_id: int,
        data: dict,
        tags: list | None = None,
        note_id: int | None = None,
        before_id: int | None = None,
        after_id: int | None = None,
    ) -> Card:
        order_key = self._resolve_position(collection_id, before_id, after_id)
        return self._repo.create(
            collection_id=collection_id,
            data=data,
            tags=tags,
            note_id=note_id,
            order_key=order_key,
        )

    def move_card(
        self,
        card_id: int,
        before_id: int | None = None,
        after_id: int | None = None,
    ) -> None:
        card = self._repo.get(card_id)
        if card is None:
            raise ValueError(f"Card {card_id} not found")
        order_key = self._resolve_position(card.collection_id, before_id, after_id)
        self._repo.update_order_key(card_id, order_key)

    def delete_card(self, card_id: int) -> None:
        self._repo.delete(card_id)

    def get_cards(
        self,
        collection_id: int,
        limit: int,
        after_key: Optional[str] = None,
    ) -> list[Card]:
        return self._repo.get_cards_after(collection_id, after_key, limit)
