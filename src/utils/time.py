import datetime
import time

from typing import Optional

MS_PER_DAY = 86_400_000

def now_ms() -> int:
    return int(time.time() * 1000)

def now_datetime() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)

def ms_to_datetime(ms: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ms / 1000, tz=datetime.timezone.utc)

def datetime_to_ms(dt: datetime.datetime) -> int:
    return int(dt.timestamp() * 1000)

def overdue_ms(due: Optional[int], now: int) -> Optional[int]:
    if due is None:
        return None
    return max(0, now - due)
