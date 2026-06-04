from datetime import datetime, timedelta, timezone, date

from src.models.node import Node
from src.schemas.node_update import NodeUpdate
from src.services.node_service import NodeService
from src.services.user_service import UserService
from src.utils.time import local_date_to_utc_ms


class RescheduleNodeUseCase:
    def __init__(
        self,
        user_service: UserService,
        node_service: NodeService,
    ):
        self._user_service = user_service
        self._node_service = node_service

    def execute(self, user_id: str, col_id: str, node_id: str, local_date_iso: str, tz_offset_min: int) -> Node:
        timestamp_ms = local_date_to_utc_ms(local_date_iso, tz_offset_min)

        tz = timezone(timedelta(minutes=tz_offset_min))
        today_local = datetime.now(tz).date()
        scheduled_day = date.fromisoformat(local_date_iso)

        if scheduled_day < today_local:
            raise ValueError("Cannot reschedule to a past day")
        if (scheduled_day - today_local).days > 365 * 100:
            raise ValueError("Cannot reschedule more than 100 years ahead")

        if self._user_service.get_pending_node(user_id) == node_id:
            self._user_service.clear_pending_node(user_id)

        return self._node_service.update(node_id, NodeUpdate(due=timestamp_ms))
        
