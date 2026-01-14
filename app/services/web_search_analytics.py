"""Web search analytics service vendored from dev/analytics.py.

Follows repository patterns:
- File-based storage with configurable directory
- Thread-safe operations using filelock
- Integration with settings for data directory
"""

import os
import json
from datetime import datetime, timedelta, timezone
from filelock import FileLock
import pandas as pd

from app.core.config import settings

# Determine data directory following repository patterns
# 1. Check for environment variable override
# 2. Use settings.WEB_SEARCH_ANALYTICS_DIR if configured
# 3. Use ./data for local development
DATA_DIR = os.getenv("WEB_SEARCH_ANALYTICS_DIR")
if not DATA_DIR:
    if hasattr(settings, "WEB_SEARCH_ANALYTICS_DIR"):
        DATA_DIR = str(settings.WEB_SEARCH_ANALYTICS_DIR)
    elif os.path.exists("/data") and os.access("/data", os.W_OK):
        DATA_DIR = "/data"
    else:
        DATA_DIR = "./data"

os.makedirs(DATA_DIR, exist_ok=True)

COUNTS_FILE = os.path.join(DATA_DIR, "web_search_request_counts.json")
TIMES_FILE = os.path.join(DATA_DIR, "web_search_request_times.json")
LOCK_FILE = os.path.join(DATA_DIR, "web_search_analytics.lock")


def _load() -> dict:
    """Load request counts from file."""
    if not os.path.exists(COUNTS_FILE):
        return {}
    with open(COUNTS_FILE) as f:
        return json.load(f)


def _save(data: dict):
    """Save request counts to file."""
    with open(COUNTS_FILE, "w") as f:
        json.dump(data, f)


def _load_times() -> dict:
    """Load request times from file."""
    if not os.path.exists(TIMES_FILE):
        return {}
    with open(TIMES_FILE) as f:
        return json.load(f)


def _save_times(data: dict):
    """Save request times to file."""
    with open(TIMES_FILE, "w") as f:
        json.dump(data, f)


async def record_request(duration: float = None, num_results: int = None) -> None:
    """
    Increment today's counter (UTC) atomically and optionally record request duration.
    
    Follows pattern from dev/analytics.py.
    """
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    with FileLock(LOCK_FILE):
        # Update counts
        data = _load()
        data[today] = data.get(today, 0) + 1
        _save(data)
        
        # Only record times for default requests (num_results=4)
        if duration is not None and (num_results is None or num_results == 4):
            times = _load_times()
            if today not in times:
                times[today] = []
            times[today].append(round(duration, 2))
            _save_times(times)


def last_n_days_df(n: int = 30) -> pd.DataFrame:
    """Return a DataFrame with a row for each of the past *n* days."""
    now = datetime.now(timezone.utc)
    with FileLock(LOCK_FILE):
        data = _load()
    records = []
    for i in range(n):
        day = (now - timedelta(days=n - 1 - i))
        day_str = day.strftime("%Y-%m-%d")
        display_date = day.strftime("%b %d")
        records.append({
            "date": display_date,
            "count": data.get(day_str, 0),
            "full_date": day_str
        })
    return pd.DataFrame(records)


def last_n_days_avg_time_df(n: int = 30) -> pd.DataFrame:
    """Return a DataFrame with average request time for each of the past *n* days."""
    now = datetime.now(timezone.utc)
    with FileLock(LOCK_FILE):
        times = _load_times()
    records = []
    for i in range(n):
        day = (now - timedelta(days=n - 1 - i))
        day_str = day.strftime("%Y-%m-%d")
        display_date = day.strftime("%b %d")
        
        day_times = times.get(day_str, [])
        avg_time = round(sum(day_times) / len(day_times), 2) if day_times else 0
        
        records.append({
            "date": display_date,
            "avg_time": avg_time,
            "request_count": len(day_times),
            "full_date": day_str
        })
    return pd.DataFrame(records)
