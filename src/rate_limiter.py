"""IP bazlı günlük rate limiting. JSON dosyası ile basit sayaç."""

import json
import threading
from datetime import date
from pathlib import Path

from src import config

_LIMIT_FILE = config.PROJECT_ROOT / "data" / "rate_limits.json"
DAILY_LIMIT = 3
_lock = threading.Lock()


def _load() -> dict:
    try:
        return json.loads(_LIMIT_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(data: dict) -> None:
    _LIMIT_FILE.parent.mkdir(exist_ok=True)
    _LIMIT_FILE.write_text(json.dumps(data), encoding="utf-8")


def get_client_ip_from_headers(headers, fallback: str = "unknown") -> str:
    """Nginx X-Real-IP → X-Forwarded-For → fallback sırasıyla gerçek IP'yi al.

    `headers` sözlük benzeri herhangi bir nesne olabilir (Streamlit'in
    st.context.headers'ı veya FastAPI'nin request.headers'ı).
    """
    real_ip = headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    forwarded = headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return fallback


def get_client_ip() -> str:
    """Streamlit ortamında gerçek IP'yi al (geriye dönük uyumluluk için)."""
    try:
        import streamlit as st
        return get_client_ip_from_headers(st.context.headers)
    except Exception:
        return "unknown"


def check_and_increment(ip: str) -> tuple[bool, int]:
    """
    Analiz hakkı varsa kullan, yoksa reddet.
    Returns: (allowed, remaining_after_use)
    """
    today = str(date.today())
    key = f"{ip}:{today}"

    with _lock:
        data = _load()
        count = data.get(key, 0)

        if count >= DAILY_LIMIT:
            return False, 0

        data[key] = count + 1
        # Bugünün dışındaki eski kayıtları temizle
        data = {k: v for k, v in data.items() if k.endswith(today)}
        _save(data)

        return True, DAILY_LIMIT - (count + 1)


def remaining_today(ip: str) -> int:
    """Bugün kaç analiz hakkı kaldığını döndür."""
    today = str(date.today())
    with _lock:
        data = _load()
        count = data.get(f"{ip}:{today}", 0)
        return max(0, DAILY_LIMIT - count)
