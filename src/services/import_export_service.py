import time

from src.db import Db
from src.models.export import FullExport
from src.repositories.import_export_repository import ImportExportRepository

class ImportExportService:
    def __init__(self, db: Db):
        self._export_repo = ImportExportRepository(db)

    def export_data(self, user_id: str) -> FullExport:
        raw_data = self._export_repo.get_full_user_data(user_id)
        now = int(time.time() * 1000)

        collections_map = {}
        for col in raw_data["collections"]:
            col_dict = col.model_dump()
            col_dict["nodes"] = []
            col_dict["reviews"] = []
            collections_map[col.id] = col_dict

        node_to_col = {}
        for node in raw_data["nodes"]:
            node_to_col[node.id] = node.collection_id
            if node.collection_id in collections_map:
                collections_map[node.collection_id]["nodes"].append(node.model_dump())

        for review in raw_data["reviews"]:
            col_id = node_to_col.get(review.node_id)
            if col_id and col_id in collections_map:
                collections_map[col_id]["reviews"].append(review.model_dump())

        return FullExport(
                    version="1.0",
                    exported_at=now,
                    user=raw_data["user"],
                    collections=list(collections_map.values())
                )

    def import_data(self, data):
        # user transaction to rollback if error and to not corrupt db
        pass
