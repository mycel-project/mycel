import time
import json

from fractional_indexing import Optional
from pydantic import TypeAdapter
from src.db import Db
from src.models.base_learning_unit import BaseLearningUnit
from src.models.learning_unit import LearningUnit
from src.models.learning_unit_position import LearningUnitPosition
from src.models.node_slot_key import NodeSlotKey


class LearningUnitRepository:
    def __init__(self, db: Db):
        self.db = db
        self.collation = "" if self.db.is_sqlite else 'COLLATE "C"'

    def _row_to_unit(self, row) -> LearningUnit:
        data = dict(row)
        unit_data = json.loads(data.pop("unit_data", "{}"))
        return TypeAdapter(LearningUnit).validate_python({
            "type": data.pop("unit_type"),
            **data,
            **unit_data
        })

    # BASIC CRUD

    def create(self, unit: LearningUnit) -> LearningUnit:                                
        self.db.execute(
            """INSERT INTO learning_units (id, node_id, unit_type, position, due, last_review, unit_data)
               VALUES (:id, :node_id, :unit_type, :position, :due, :last_review, :unit_data)""",
            {
                "id": unit.id,
                "node_id": unit.node_id,
                "unit_type": unit.type,
                "position": unit.position,
                "slot": unit.slot,
                "due": unit.due,
                "last_review": unit.last_review,
                "unit_data": unit.model_dump_json(exclude=set(BaseLearningUnit.model_fields.keys())),
            },
        )
        return unit

    def get(self, unit_id: str) -> Optional[LearningUnit]:
        row = self.db.fetch_one(
            "SELECT * FROM learning_units WHERE id = :id", 
            {"id": unit_id}
        )
        return self._row_to_unit(row) if row else None

    def get_by_node(self, node_id: str) -> list[LearningUnit]:
        rows = self.db.fetch_all(
            "SELECT * FROM learning_units WHERE node_id = :id",
            {"id": node_id},
        )
        return [self._row_to_unit(row) for row in rows]

    def get_by_nodes(self, node_ids: list[str]) -> list[LearningUnit]:
        if not node_ids:
            return []
        placeholders = ", ".join(f":id_{i}" for i in range(len(node_ids)))
        params = {f"id_{i}": node_id for i, node_id in enumerate(node_ids)}
        rows = self.db.fetch_all(
            f"SELECT * FROM learning_units WHERE node_id IN ({placeholders})",
            params,
        )
        return [self._row_to_unit(row) for row in rows]

    def update(self, unit: LearningUnit) -> None:
        self.db.execute(
            """UPDATE learning_units 
               SET unit_type = :unit_type, position = :position, due = :due, 
                   last_review = :last_review, unit_data = :unit_data
               WHERE node_id = :node_id""",
            {
                "node_id": unit.node_id,
                "unit_type": unit.type,
                "position": unit.position,
                "due": unit.due,
                "last_review": unit.last_review,
                "unit_data": unit.model_dump_json(exclude=set(BaseLearningUnit.model_fields.keys())),
            },
        )

    def delete(self, id: str) -> None:
        self.db.execute("DELETE FROM learning_units WHERE id = :id", {"id": id})

    # DOMAIN

    def get_position(self, unit_id: str) -> Optional[str]:
        row = self.db.fetch_one("SELECT position FROM learning_units WHERE id = :id", {"id": unit_id})
        return row["position"] if row else None

    def get_all_positions(self, collection_id: str) -> list[tuple[str, str]]:
            query = """
                SELECT lu.id, lu.position 
                FROM learning_units lu
                JOIN nodes n ON lu.node_id = n.id
                WHERE n.collection_id = :col_id 
                AND n.deleted_at IS NULL
            """
            rows = self.db.fetch_all(query, {"col_id": collection_id})

            return [(row["id"], row["position"]) for row in rows]

    def get_all_positions_with_node(self, collection_id: str) -> list[LearningUnitPosition]:
        query = """
            SELECT lu.node_id, lu.slot, lu.position 
            FROM learning_units lu
            JOIN nodes n ON lu.node_id = n.id
            WHERE n.collection_id = :col_id 
            AND n.deleted_at IS NULL
            ORDER BY lu.position
        """
        rows = self.db.fetch_all(query, {"col_id": collection_id})
        return [
            LearningUnitPosition(
                node_slot_key=NodeSlotKey(node_id=row["node_id"], slot=row["slot"]),
                position=row["position"]
            )
            for row in rows
        ]
        
    def count_before_position(self, collection_id: str, position: str) -> int:
        query = f"""
            SELECT COUNT(*) as count 
            FROM learning_units lu
            JOIN nodes n ON lu.node_id = n.id
            WHERE n.collection_id = :col_id 
              AND lu.position {self.collation} < :position 
              AND n.deleted_at IS NULL
        """
        row = self.db.fetch_one(query, {"col_id": collection_id, "position": position})
        return row["count"] if row else 0
    
    def count_by_collection(self, collection_id: str) -> int:
        query = """
            SELECT COUNT(*) as count 
            FROM learning_units lu
            JOIN nodes n ON lu.node_id = n.id
            WHERE n.collection_id = :col_id 
              AND n.deleted_at IS NULL
        """
        row = self.db.fetch_one(query, {"col_id": collection_id})
        return row["count"] if row else 0

    def get_position_at_offset(self, collection_id: str, offset: int) -> Optional[str]:
            query = f"""
                SELECT lu.position 
                FROM learning_units lu
                JOIN nodes n ON lu.node_id = n.id
                WHERE n.collection_id = :col_id 
                  AND n.deleted_at IS NULL 
                ORDER BY lu.position {self.collation} 
                LIMIT 1 OFFSET :offset
            """
            row = self.db.fetch_one(query, {"col_id": collection_id, "offset": offset})
            return row["position"] if row else None

    def get_tail_key(self, collection_id: str) -> Optional[str]:
        """Get the last position in the collection, ordered lexicographically.""" 
        query = f"""
            SELECT lu.position 
            FROM learning_units lu
            JOIN nodes n ON lu.node_id = n.id
            WHERE n.collection_id = :col_id 
              AND n.deleted_at IS NULL 
            ORDER BY lu.position {self.collation} DESC 
            LIMIT 1
        """
        row = self.db.fetch_one(query, {"col_id": collection_id})
        return row["position"] if row else None

 
    def get_dues(self, collection_id: str, now_ms: Optional[int] = None) -> list[LearningUnit]:
        now_ms = now_ms or int(time.time() * 1000)
        
        query = """
            SELECT lu.* FROM learning_units lu
            JOIN nodes n ON lu.node_id = n.id
            WHERE n.collection_id = :col_id 
              AND lu.due <= :now_ms 
            ORDER BY lu.due
        """
        rows = self.db.fetch_all(query, {"col_id": collection_id, "now_ms": now_ms})
        
        return [self._row_to_unit(dict(row)) for row in rows]
    
    def update_position(self, unit_id: str, position: str) -> None:
        self.db.execute(
            "UPDATE learning_units SET position = :position WHERE id = :id",
            {"position": position, "id": unit_id},
        )

    def due_count_by_type_and_day(self, collection_id: str, start_ms: int, to_ms: int, tz_offset_minutes: int = 0) -> list[tuple[int, str, int]]:
        """
        day_start_ms is UTC midnight of the local day (i.e. local midnight expressed in UTC).
        e.g. for UTC+1, May 20 local → 2026-05-19 23:00:00 UTC.
        """
        tz_offset_ms = tz_offset_minutes * 60_000
        dismiss_filter = (
            "json_extract(lu.unit_data, '$.dismiss') = 1"
            if self.db.is_sqlite
            else "lu.unit_data::jsonb->>'dismiss' = 'true'"
        )
        rows = self.db.fetch_all(
            f"""
            SELECT
                (CAST((lu.due + :tz) AS BIGINT) / 86400000) * 86400000 - :tz AS day_start_ms,
                lu.unit_type,
                COUNT(*) as count
            FROM learning_units lu
            JOIN nodes n ON lu.node_id = n.id
            WHERE n.collection_id = :col_id
              AND lu.due >= :start_ms
              AND lu.due < :to_ms
              AND n.deleted_at IS NULL
              AND NOT (lu.unit_type = 'fragment' AND {dismiss_filter})
            GROUP BY day_start_ms, lu.unit_type
            ORDER BY day_start_ms
            """,
            {"tz": tz_offset_ms, "col_id": collection_id, "start_ms": start_ms, "to_ms": to_ms},
        )
        return [(row["day_start_ms"], row["unit_type"], row["count"]) for row in rows]

    # unused?
    # def get_predecessor_position(self, collection_id: str, position: str, exclude_id: str) -> Optional[str]:
    #     query = f"""
    #         SELECT lu.position 
    #         FROM learning_units lu
    #         JOIN nodes n ON lu.node_id = n.id
    #         WHERE n.collection_id = :col_id 
    #           AND lu.position {self.collation} < :position 
    #           AND lu.id != :exclude_id 
    #           AND n.deleted_at IS NULL
    #         ORDER BY lu.position {self.collation} DESC 
    #         LIMIT 1
    #     """
    #     row = self.db.fetch_one(query, {"col_id": collection_id, "position": position, "exclude_id": exclude_id})
    #     return row["position"] if row else None
    # def get_successor_position(self, collection_id: str, position: str, exclude_id: str) -> Optional[str]:
    #     query = f"""
    #         SELECT lu.position 
    #         FROM learning_units lu
    #         JOIN nodes n ON lu.node_id = n.id
    #         WHERE n.collection_id = :col_id 
    #           AND lu.position {self.collation} > :position 
    #           AND lu.id != :exclude_id 
    #           AND n.deleted_at IS NULL
    #         ORDER BY lu.position {self.collation} ASC 
    #         LIMIT 1
    #     """
    #     row = self.db.fetch_one(query, {"col_id": collection_id, "position": position, "exclude_id": exclude_id})
    #     return row["position"] if row else None
    # def update_last_review(self, unit_id: str) -> None:
    #         now = int(time.time() * 1000)
    #         self.db.execute(
    #             "UPDATE learning_units SET last_review = :now WHERE id = :id",
    #             {"now": now, "id": unit_id},
    #         )
