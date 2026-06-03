from datetime import datetime, timedelta, timezone, date

from src.models.node import Node
from src.schemas.node_update import NodeUpdate
from src.services.cache.pending_review_cache import PendingReviewCache
from src.services.node_service import NodeService
from src.utils.time import local_date_to_utc_ms


class RescheduleNodeUseCase:
    def __init__(
        self,
        node_service: NodeService,
        pending_review_cache: PendingReviewCache,
    ):
        self._node_service = node_service
        self._pending_review_cache = pending_review_cache

    def execute(self, col_id: str, node_id: str, local_date_iso: str, tz_offset_min: int) -> Node:
        timestamp_ms = local_date_to_utc_ms(local_date_iso, tz_offset_min)

        tz = timezone(timedelta(minutes=tz_offset_min))
        today_local = datetime.now(tz).date()
        scheduled_day = date.fromisoformat(local_date_iso)

        if scheduled_day < today_local:
            raise ValueError("Cannot reschedule to a past day")
        if (scheduled_day - today_local).days > 365 * 100:
            raise ValueError("Cannot reschedule more than 100 years ahead")

        if self._pending_review_cache.get() == node_id:
            self._pending_review_cache.clear()

        return self._node_service.update(node_id, NodeUpdate(due=timestamp_ms))
        
