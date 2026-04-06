from typing import Optional

from src.db import Db
from src.models.card import Card
from src.repositories.card_repository import CardRepository
from src.services.ordering_service import insert_between, spread_keys
from src.models.card_list_view import CardListView


class CardService:
    """
    Card service logic (higher level than card_repository)
    """
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

    def reprioritise_card(
        self,
        card_id: int,
        new_position_card_id: int | None = None,
    ) -> None:
        if new_position_card_id is None:
            raise ValueError("new_position_card_id is required")
        card = self._repo.get(card_id)
        if card is None:
            raise ValueError(f"Card {card_id} not found")
        new_position_card = self._repo.get(new_position_card_id)
        if new_position_card is None:
            raise ValueError(f"Card {new_position_card_id} not found")
        card_key: str = card.order_key or ""
        target_key: str = new_position_card.order_key or ""
        if not card_key or not target_key:
            raise ValueError("Cards must have order_key set before reprioritising")

        moving_forward = card_key < target_key

        if moving_forward:
            # Card moves to a higher index: after removing it, the target card
            # shifts one position earlier, so we insert AFTER the target.
            successor_key = self._repo.get_successor_key(
                card.collection_id,
                target_key,
                exclude_id=card_id,
            )
            order_key = insert_between(target_key, successor_key)
        else:
            # Card moves to a lower index: target position is unaffected by the
            # removal, so we insert BEFORE the target.
            predecessor_key = self._repo.get_predecessor_key(
                card.collection_id,
                target_key,
                exclude_id=card_id,
            )
            order_key = insert_between(predecessor_key, target_key)

        self._repo.update_order_key(card_id, order_key)

    def reindex(self, collection_id: int) -> None:
        """Redistribute all order_keys evenly to avoid key bloat."""
        entries = self._repo.get_all_order_keys(collection_id)
        if not entries:
            return
        new_keys = spread_keys(len(entries))
        for (card_id, _), new_key in zip(entries, new_keys):
            self._repo.update_order_key(card_id, new_key)

    def delete_card(self, card_id: int) -> None:
        self._repo.delete(card_id)

    def get_cards(
        self,
        collection_id: int,
        limit: int,
        after_key: Optional[str] = None,
    ) -> list[CardListView]:
        cards = self._repo.get_cards_after(collection_id, after_key, limit)
        print([card.order_key for card in cards])
        return [
            CardListView(
                id=c.id,
                collection_id=c.collection_id,
                type=c.type,
                data=c.data,
                position=i
            )
            for i, c in enumerate(cards)
        ]
