import datetime
import time

from typing import Optional

MS_PER_DAY = 86_400_000

def now_ms() -> int:
    return int(time.time() * 1000)

def now_s() -> int:
    return int(time.time())

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

def add_days_ms(now: int, days: int) -> int:
    return now + days * MS_PER_DAY

def local_date_to_utc_ms(date_iso: str, tz_offset_minutes: int) -> int:
    """
    Converts a local date to the UTC timestamp (ms) of midnight on that day.
    e.g. "2026-05-20" with tz_offset=60 (UTC+1) → 2026-05-19 23:00:00 UTC in ms (so 1779231600000).
    """
    tz = datetime.timezone(datetime.timedelta(minutes=tz_offset_minutes))
    dt = datetime.datetime.strptime(date_iso, "%Y-%m-%d").replace(tzinfo=tz)
    return int(dt.timestamp() * 1000)

def start_of_local_day_ms(ts_ms: int, tz_offset_minutes: int = 0) -> int:
    tz = datetime.timezone(datetime.timedelta(minutes=tz_offset_minutes))
    dt = datetime.datetime.fromtimestamp(ts_ms / 1000, tz=tz)
    midnight = datetime.datetime(dt.year, dt.month, dt.day, tzinfo=tz)
    return int(midnight.timestamp() * 1000)

def start_of_local_today_ms(tz_offset_minutes: int = 0) -> int:
    tz = datetime.timezone(datetime.timedelta(minutes=tz_offset_minutes))
    now = datetime.datetime.now(tz)
    midnight = datetime.datetime(now.year, now.month, now.day, tzinfo=tz)
    return int(midnight.timestamp() * 1000)

def start_of_local_tomorrow_ms(tz_offset_minutes: int = 0) -> int:
    tz = datetime.timezone(datetime.timedelta(minutes=tz_offset_minutes))
    today_ms = start_of_local_today_ms(tz_offset_minutes)
    today = datetime.datetime.fromtimestamp(today_ms / 1000, tz=tz)
    return int((today + datetime.timedelta(days=1)).timestamp() * 1000)
