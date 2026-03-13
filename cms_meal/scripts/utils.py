import time
from typing import Any, Dict

import requests


def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({
        "User-Agent": "cms-meal-data-associate/1.0"
    })
    return session


def get_json(session: requests.Session, url: str, params: Dict[str, Any] | None = None, retries: int = 3) -> Any:
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            resp = session.get(url, params=params, timeout=60)
            if resp.status_code == 429:
                time.sleep(2 * attempt)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            time.sleep(1.5 * attempt)
    raise RuntimeError(f"Failed to fetch {url} after {retries} tries: {last_err}")
