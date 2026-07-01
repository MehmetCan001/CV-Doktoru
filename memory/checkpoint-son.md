# CHECKPOINT — 2026-07-01 — v1.5

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.
**URL:** https://cvdoktoru.com ✅ CANLI

## Tech Stack (Mevcut)
- **Frontend/UI**: Streamlit (`src/app.py`) — TERK EDİLECEK
- **AI Motoru**: Anthropic Claude (`src/_analyzer_claude.py`) — `claude-sonnet-4-6`
- **Dosya Okuma**: `src/pdf_reader.py` — PDF, DOCX, düz metin
- **Prompt Sistemi**: `src/prompt_loader.py`
- **Config**: `src/config.py` — MAX_TOKENS=32768, _TIMEOUT=600s
- **Sunucu**: Hetzner CX23, Nuremberg — IP: 46.225.20.111
- **Servis**: systemd `cv-doktoru.service`
- **Reverse proxy**: Nginx + Let's Encrypt HTTPS
- **Domain**: GoDaddy `cvdoktoru.com`

## Hedef Tech Stack (Yarın)
- **Frontend**: Vanilla HTML/CSS/JS (`templates/index.html`)
- **Backend**: FastAPI (`src/server.py`)
- **Streaming**: Server-Sent Events (SSE) — token token anlık çıktı
- **Python analiz kodu**: Değişmez

## Tamamlanan
- [x] Temel CV + iş ilanı analizi (Claude API)
- [x] Prompt sistemi (13 bölüm, koşullu bölümler)
- [x] Hetzner VPS deploy
- [x] HTTPS (Let's Encrypt)
- [x] IP bazlı rate limiting (3/gün)
- [x] Loading animasyonu (CSS)
- [x] Prompt kısaltma (~%30 daha hızlı)
- [x] threading.Thread ile event loop izolasyonu
- [x] Dosya kalıcılığı (WebSocket kopsa raporu kurtar)

## Streamlit Sorunları (Neden Terk Ediyoruz)
1. WebSocket drop — uzun analiz sırasında bağlantı kopuyor
2. Event loop çakışması — Anthropic SDK ile Streamlit asyncio çakışıyor
3. Mobil dosya yükleme — seçim oluyor ama upload tamamlanmıyor
4. UI kısıtı — tam CSS kontrolü yok
5. Streaming yapısal olarak güvenilmez

## Yarınki Plan: Streamlit → FastAPI
1. `src/server.py` — FastAPI uygulaması
   - `GET /` → index.html
   - `POST /analyze` → SSE stream (token token çıktı)
   - `POST /upload` → CV dosyası parse
2. `templates/index.html` — mevcut tasarımı port et
3. `requirements.txt` — fastapi ekle (uvicorn zaten var)
4. Systemd → `uvicorn src.server:app --port 8501`
5. Nginx → değişiklik yok (aynı port)
6. Test: masaüstü + mobil

## Analiz Kodu (Dokunmayacak)
- `src/analyzer.py` — CVDoctor wrapper
- `src/_analyzer_claude.py` — threading.Thread + streaming
- `src/prompt_loader.py` — prompt dosyaları yükle
- `src/pdf_reader.py` — PDF/DOCX okuma
- `src/rate_limiter.py` — IP rate limiting
- `prompts/` — tüm prompt dosyaları
- `knowledge/` — Türk iş kültürü bilgi tabanı

## Bilinen Sorunlar
- Streamlit: analiz tamamlanıyor ama WebSocket drop nedeniyle rapor ekrana gelmiyor
- Mobil: dosya upload tamamlanmıyor (Streamlit sorunu, FastAPI ile çözülecek)
- `data/last_report.txt` — geçici workaround, FastAPI'ye geçince kaldırılacak
