"""
CV Doktoru — FastAPI backend.

Başlatmak için:
    uvicorn src.server:app --host 0.0.0.0 --port 8501
"""

import os
import re
import tempfile
import threading
import time
import uuid
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.concurrency import run_in_threadpool

from src import analytics, config
from src.analyzer import CVDoctor
from src.pdf_export import generate_pdf_report
from src.pdf_reader import extract_text_from_docx, extract_text_from_pdf
from src.rate_limiter import (
    DAILY_LIMIT,
    check_and_increment,
    get_client_ip_from_headers,
    remaining_today,
)

load_dotenv()

TEMPLATES_DIR = config.PROJECT_ROOT / "templates"

app = FastAPI(title="CV Doktoru")

# Analiz işleri arka planda yürütülür, tarayıcı sonucu poll ile sorgular.
# Tek bir uzun HTTP bağlantısı NAT/firewall tarafından "boşta" sayılıp
# kesilebiliyor (2026-07-02'de PC tarayıcısında ERR_CONNECTION_RESET ile
# doğrulandı) — polling, hiçbir tekil bağlantının dakikalarca açık kalmasını
# gerektirmediği için bu sorunu kökten çözer.
_JOB_TTL_SECONDS = 30 * 60
_jobs: dict[str, dict] = {}
_jobs_lock = threading.Lock()


def _prune_old_jobs() -> None:
    cutoff = time.time() - _JOB_TTL_SECONDS
    stale = [jid for jid, job in _jobs.items() if job["created"] < cutoff]
    for jid in stale:
        del _jobs[jid]


def _round_score(report: str) -> str:
    """Rapordaki X/100 skorunu en yakın 5'e yuvarlar (LLM varyansını gizler)."""
    def _replace(m):
        rounded = round(int(m.group(1)) / 5) * 5
        return f"**{rounded}/100**"
    return re.sub(r"\*\*(\d+)/100\*\*", _replace, report)


def _client_ip(request: Request) -> str:
    fallback = request.client.host if request.client else "unknown"
    return get_client_ip_from_headers(request.headers, fallback)


SITE_URL = os.getenv("SITE_URL", "https://cvdoktoru.com").rstrip("/")


@app.get("/", response_class=HTMLResponse)
def index():
    return (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/robots.txt", response_class=Response)
def robots_txt():
    body = f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n"
    return Response(content=body, media_type="text/plain")


@app.get("/sitemap.xml", response_class=Response)
def sitemap_xml():
    today = time.strftime("%Y-%m-%d")
    body = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{SITE_URL}/</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "    <priority>1.0</priority>\n"
        "  </url>\n"
        "</urlset>\n"
    )
    return Response(content=body, media_type="application/xml")


@app.get("/api/remaining")
def api_remaining(request: Request):
    ip = _client_ip(request)
    return {"remaining": remaining_today(ip), "limit": DAILY_LIMIT}


@app.post("/api/track/visit")
def api_track_visit(request: Request):
    analytics.log_event("page_view", _client_ip(request))
    return {"ok": True}


@app.post("/api/track/premium-click")
def api_track_premium_click(request: Request):
    analytics.log_event("premium_click", _client_ip(request))
    return {"ok": True}


@app.post("/api/leads")
def api_leads(email: str = Form(...)):
    ok = analytics.record_lead(email)
    if not ok:
        return JSONResponse({"error": "Geçerli bir e-posta adresi girin."}, status_code=400)
    return {"ok": True}


@app.get("/api/analytics/summary")
def api_analytics_summary(request: Request, key: str = "", days: int = 14):
    admin_key = os.getenv("ANALYTICS_ADMIN_KEY")
    if not admin_key or key != admin_key:
        return JSONResponse({"error": "Yetkisiz."}, status_code=403)
    return analytics.summary(days=days)


def _run_analysis_job(job_id: str, cv_text: str, job_text: str) -> None:
    doctor = CVDoctor()
    try:
        report = doctor.analyze(cv_text, job_text)
        report = _round_score(report)
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = f"Analiz hatası ({type(e).__name__}): {e}"
        return

    try:
        report_file = config.DATA_DIR / "last_report.txt"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report, encoding="utf-8")
    except Exception:
        pass

    with _jobs_lock:
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["report"] = report


@app.post("/api/analyze/start")
async def api_analyze_start(
    request: Request,
    job_text: str = Form(...),
    cv_text: str = Form(""),
    cv_file: UploadFile | None = File(None),
):
    text = cv_text.strip()

    if cv_file is not None and cv_file.filename:
        suffix = Path(cv_file.filename).suffix.lower()
        if suffix not in (".pdf", ".docx"):
            return JSONResponse(
                {"error": f"Desteklenmeyen dosya formatı: {suffix}"}, status_code=400
            )

        content = await cv_file.read()
        if len(content) > 10 * 1024 * 1024:
            return JSONResponse({"error": "Dosya çok büyük (maks. 10 MB)."}, status_code=400)

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            text = (
                extract_text_from_pdf(tmp_path)
                if suffix == ".pdf"
                else extract_text_from_docx(tmp_path)
            )
        except Exception as e:
            return JSONResponse({"error": f"Dosya okunamadı: {e}"}, status_code=400)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    if not text.strip():
        return JSONResponse(
            {"error": "Lütfen bir CV yükleyin veya CV metnini yapıştırın."}, status_code=400
        )
    if not job_text.strip():
        return JSONResponse({"error": "Lütfen iş ilanı metnini girin."}, status_code=400)

    ip = _client_ip(request)
    allowed, remaining = check_and_increment(ip)
    if not allowed:
        return JSONResponse(
            {
                "error": (
                    f"Bugünkü ücretsiz analiz hakkınızı kullandınız (günlük {DAILY_LIMIT} analiz). "
                    "Yarın gece yarısı UTC'de yenilenir."
                )
            },
            status_code=429,
        )

    if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("GEMINI_API_KEY")):
        return JSONResponse({"error": "API anahtarı sunucuda bulunamadı."}, status_code=500)

    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _prune_old_jobs()
        _jobs[job_id] = {"status": "running", "report": None, "error": None, "created": time.time()}

    thread = threading.Thread(
        target=_run_analysis_job, args=(job_id, text, job_text.strip()), daemon=True
    )
    thread.start()

    return {"job_id": job_id, "remaining": remaining}


@app.get("/api/analyze/status/{job_id}")
def api_analyze_status(job_id: str):
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            return JSONResponse({"error": "İş bulunamadı veya süresi doldu."}, status_code=404)
        return {"status": job["status"], "report": job["report"], "error": job["error"]}


@app.post("/api/pdf")
async def api_pdf(report: str = Form(...)):
    try:
        pdf_bytes = await run_in_threadpool(generate_pdf_report, report)
    except RuntimeError as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=cv_analiz_raporu.pdf"},
    )
