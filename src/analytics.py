"""Fake-door testi için basit, çerezsiz, sunucu-taraflı sayaç.

Üçüncü taraf analytics kullanılmaz (marka vaadi: "verileriniz saklanmaz").
IP adresleri ham olarak saklanmaz; sadece günlük tekrar-tıklama tespiti için
tuzlanmış kısa bir hash tutulur, ham IP hiçbir dosyaya yazılmaz.
"""

import hashlib
import json
import os
import re
import threading
from datetime import date, datetime, timedelta
from pathlib import Path

from src import config

_EVENTS_FILE = config.DATA_DIR / "analytics_events.jsonl"
_LEADS_FILE = config.DATA_DIR / "leads.json"
_lock = threading.Lock()

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

VALID_EVENTS = {"page_view", "premium_click"}


def _ip_hash(ip: str) -> str:
    salt = os.getenv("ANALYTICS_SALT", "cv-doktoru-varsayilan-tuz")
    return hashlib.sha256(f"{salt}:{ip}".encode("utf-8")).hexdigest()[:16]


def log_event(event: str, ip: str) -> None:
    """Bir sayfa görüntüleme / buton tıklaması olayını append-only log'a yazar."""
    if event not in VALID_EVENTS:
        return
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "day": str(date.today()),
        "event": event,
        "ip_hash": _ip_hash(ip),
    }
    with _lock:
        _EVENTS_FILE.parent.mkdir(exist_ok=True)
        with _EVENTS_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def record_lead(email: str) -> bool:
    """89 TL'lik premium özelliğe ilgi duyan kullanıcının e-postasını kaydeder.

    Returns: e-posta geçerliyse ve kaydedildiyse True, aksi halde False.
    """
    email = email.strip().lower()
    if not email or not _EMAIL_RE.match(email) or len(email) > 254:
        return False

    with _lock:
        _LEADS_FILE.parent.mkdir(exist_ok=True)
        try:
            leads = json.loads(_LEADS_FILE.read_text(encoding="utf-8"))
        except Exception:
            leads = []

        if any(entry.get("email") == email for entry in leads):
            return True  # zaten kayıtlı, hata değil

        leads.append({"email": email, "ts": datetime.utcnow().isoformat()})
        _LEADS_FILE.write_text(json.dumps(leads, ensure_ascii=False, indent=2), encoding="utf-8")
        return True


def summary(days: int = 14) -> dict:
    """Son N gün için tekil ziyaretçi, tıklama ve lead sayılarını özetler."""
    cutoff = date.today() - timedelta(days=days - 1)

    page_view_hashes: set[str] = set()
    premium_click_hashes: set[str] = set()

    if _EVENTS_FILE.exists():
        with _EVENTS_FILE.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entry_day = date.fromisoformat(entry["day"])
                except Exception:
                    continue
                if entry_day < cutoff:
                    continue
                key = f'{entry["day"]}:{entry["ip_hash"]}'
                if entry["event"] == "page_view":
                    page_view_hashes.add(key)
                elif entry["event"] == "premium_click":
                    premium_click_hashes.add(key)

    try:
        leads = json.loads(_LEADS_FILE.read_text(encoding="utf-8"))
    except Exception:
        leads = []

    lead_count = sum(
        1 for entry in leads
        if datetime.fromisoformat(entry["ts"]).date() >= cutoff
    )

    unique_visitors = len(page_view_hashes)
    unique_clickers = len(premium_click_hashes)
    click_rate_pct = round(100 * unique_clickers / unique_visitors, 1) if unique_visitors else 0.0

    verdict, verdict_detail = _decision_matrix(unique_visitors, click_rate_pct)

    return {
        "days": days,
        "unique_visitors": unique_visitors,
        "premium_click_visitors": unique_clickers,
        "leads_captured": lead_count,
        "total_leads_all_time": len(leads),
        "click_rate_pct": click_rate_pct,
        "lead_conversion_pct": round(100 * lead_count / unique_visitors, 1) if unique_visitors else 0.0,
        "verdict": verdict,
        "verdict_detail": verdict_detail,
    }


# Karar matrisi: CTA tıklama oranına (tıklayan tekil ziyaretçi / toplam tekil ziyaretçi)
# göre otomatik değerlendirme. Eşikler yüzdeye dayalı — trafik hacmi haftadan haftaya
# değişse de aynı mantık geçerli kalır.
_MIN_SAMPLE_SIZE = 30  # bu sayının altında rakamlar gürültülü, karar verilmez


def _decision_matrix(unique_visitors: int, click_rate_pct: float) -> tuple[str, str]:
    if unique_visitors < _MIN_SAMPLE_SIZE:
        return (
            "YETERSİZ_VERİ",
            f"Henüz {unique_visitors} tekil ziyaretçi var, en az {_MIN_SAMPLE_SIZE} gerekli — "
            "rakamlar bu hacimde güvenilir değil, beklemeye devam edin.",
        )
    if click_rate_pct < 1:
        return (
            "KILL",
            "Tıklama oranı %1'in altında — pazar sinyali zayıf. Pivot yapın veya projeyi "
            "sıfır kod israfıyla bırakın.",
        )
    if click_rate_pct <= 5:
        return (
            "OPTIMIZE",
            "Tıklama oranı %1-5 arasında — metni, hero kancasını veya fiyatı değiştirip "
            "3-4 gün daha test edin.",
        )
    return (
        "GREEN_LIGHT",
        "Tıklama oranı %5'in üzerinde — pazar talebi doğrulandı. MVP mimarisine geçilebilir.",
    )
