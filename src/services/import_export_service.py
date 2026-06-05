import time
import logging
from datetime import datetime, timezone

from sqlalchemy.exc import IntegrityError

from src.core.app_infos import AppInfos
from src.db import Db
from src.domain.domain_exceptions import DataExportError, DataImportError
from src.models.export import FullExport
from src.repositories.import_export_repository import ImportExportRepository


logger = logging.getLogger(__name__)

class ImportExportService:
    def __init__(self, db: Db, app_infos: AppInfos):
        self._export_repo = ImportExportRepository(db)
        self._app_infos = app_infos

    def export_data(self, user_id: str) -> FullExport:
        try:
            raw_data = self._export_repo.get_full_user_data(user_id)
            now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

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
                        version=self._app_infos.version,
                        exported_at=now,
                        user=raw_data["user"],
                        collections=list(collections_map.values())
                    )
        except Exception as e:
            logger.error(f"Export failed for user {user_id}: {str(e)}")
            raise DataExportError(message="An unexpected error occurred during import.")

    def import_data(self, user_id: str, data):
        try:
            data.user.id = user_id
            self._export_repo.import_full_user_data(data)
        except IntegrityError:
            raise DataImportError(message="Conflict: Please delete your existing data before importing.")
        except Exception as e:
            logger.error(f"Import failed for user {user_id}: {str(e)}. Tables incompatibility ?")
            raise DataImportError(message="An unexpected error occurred during import.")
