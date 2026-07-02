"""
CV Doktoru — FastAPI backend.

Başlatmak için:
    uvicorn src.server:app --host 0.0.0.0 --port 8501
"""

import os
import re
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, Response
from starlette.concurrency import run_in_threadpool

from src import config
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


def _round_score(report: str) -> str:
    """Rapordaki X/100 skorunu en yakın 5'e yuvarlar (LLM varyansını gizler)."""
    def _replace(m):
        rounded = round(int(m.group(1)) / 5) * 5
        return f"**{rounded}/100**"
    return re.sub(r"\*\*(\d+)/100\*\*", _replace, report)


def _client_ip(request: Request) -> str:
    fallback = request.client.host if request.client else "unknown"
    return get_client_ip_from_headers(request.headers, fallback)


@app.get("/", response_class=HTMLResponse)
def index():
    return (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/api/remaining")
def api_remaining(request: Request):
    ip = _client_ip(request)
    return {"remaining": remaining_today(ip), "limit": DAILY_LIMIT}


@app.post("/api/analyze")
async def api_analyze(
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

    doctor = CVDoctor()
    try:
        report = await run_in_threadpool(doctor.analyze, text, job_text.strip())
        report = _round_score(report)
    except Exception as e:
        return JSONResponse(
            {"error": f"Analiz hatası ({type(e).__name__}): {e}"}, status_code=500
        )

    try:
        report_file = config.DATA_DIR / "last_report.txt"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report, encoding="utf-8")
    except Exception:
        pass

    return {"report": report, "remaining": remaining}


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
