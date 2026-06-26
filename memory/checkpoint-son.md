# CHECKPOINT — 2026-06-26 — v1.2

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.

## Tech Stack
- **Frontend:** Streamlit (`src/app.py`)
- **AI Motoru:** Anthropic Claude (`src/_analyzer_claude.py`) — `claude-sonnet-4-6`
- **Dosya Okuma:** `src/pdf_reader.py` — PDF, DOCX, düz metin
- **Prompt Sistemi:** `src/prompt_loader.py`
- **Config:** `src/config.py` — MAX_TOKENS=32768, _TIMEOUT=300s
- **Prompt Dosyaları:** `prompts/` (system_prompt.md, analysis_prompt.md, examples/)
- **Bilgi Tabanı:** `knowledge/turk_is_kulturu.md`

## Tamamlanan Modüller
- [x] Temel CV + iş ilanı analizi
- [x] PDF/DOCX/metin dosyası okuma
- [x] Streamlit UI — hero, form, rapor gösterimi, PDF/TXT indirme
- [x] Prompt sistemi — system_prompt + few-shot + analysis_prompt
- [x] Tüm rapor bölümleri (13 bölüm)
- [x] Koşullu bölümler (ALTERNATİF HEDEFLER skor<30, MÜLAKAT HAZIRLIĞI skor≥40)
- [x] Claude API geçişi — ANTHROPIC_API_KEY ✅
- [x] Streamlit Cloud deploy — aktif
- [x] Skor yuvarlama — `_round_score()` ile 5'e yuvarla
- [x] Premium SaaS UI redesign
- [x] **MAX_TOKENS 32768** (16384'de kesiliyordu)
- [x] **Streaming tamamen kaldırıldı** → blocking mode
- [x] **st.stop() with bloğu dışına taşındı** — report=None ile önceden init
- [x] **st.rerun() kaldırıldı** — WebSocket yenilenmesinde session_state kayboluyordu
- [x] **st.status() kaldırıldı** — blocking API çağrısında UI güncellemiyordu
- [x] **st.info() placeholder** ile analiz öncesi/sonrası mesaj (basit ve güvenilir)

## Mevcut Durum
- **Faz:** Bug fix — rapor ekranda görünmeme sorunu
- **Son commit:** `f439921` — st.status() kaldırıldı, st.info/success akışı
- **Deploy:** Streamlit Cloud'a push edildi, **test bekleniyor (yarın)**
- **Analiz modu:** Blocking (`doctor.analyze()`) — streaming yok
- **Çalıştırma:** `python -m streamlit run src/app.py` → http://localhost:8501

## Alınan Mimari Kararlar
1. **MAX_TOKENS = 32768** — Türkçe + detaylı format çıktıyı 10K-16K token'a çıkarıyor
2. **_TIMEOUT = 300s** — büyük promptlar 2-4 dk sürebilir (eskiden 180s)
3. **Streaming YOK** — Streamlit'te uzun LLM çağrıları için yapısal olarak güvenilmez
4. **st.status() YOK** — blocking API çağrısında Streamlit Cloud'da UI güncellemesi çalışmıyor
5. **st.rerun() YOK** — uzun API çağrısı sırasında WebSocket yenilenirse session_state boş gelir
6. **st.info() placeholder** — `_notice = st.info(...)` → `_notice.success(...)` güvenilir tek yol
7. **Fall-through rendering** — analiz biter bitmez aynı script akışında rapor render edilir
8. **Few-shot: 2 örnek** — orta uyum (ornek_1) + yanlış sektör (ornek_2)

## Açık Kalan / Sonraki Adımlar
1. **BUG FIX TEST** — st.status() kaldırma fix'i deploy edildi, **yarın test edilecek**
2. **Domain bağlama** — `cvdoktoru.com.tr` GoDaddy'den alındı; CNAME → Streamlit Cloud
3. **LinkedIn profil önerisi bölümü** — yol haritasında 1 numara
4. **Yazım kalitesi boyutu** — Grammarly'den ilham
5. **Mobil test** — 2 kolon layout mobilde test edilmedi

## Bu Oturumda Öğrenilenler (CLAUDE.md'ye Eklendi)
- Streamlit streaming yapısal olarak güvenilmez → ASLA kullanma
- `st.stop()` `with` bloğu içinde güvenilmez → dışarıda çağır
- `st.rerun()` + uzun API çağrısı = WebSocket yenilenir, session_state kaybolur
- `st.status()` blocking API çağrısında Streamlit Cloud'da UI güncellemez
- **Güvenilir pattern:** `_notice = st.info(...)` → analiz → `_notice.success(...)` → fall-through render
- Commitler push edilmeden Streamlit Cloud deploy olmaz (bu oturumda push unutulmuştu)

## Bilinen Sorunlar
- st.info() fix'i henüz kullanıcı tarafından test edilmedi — yarın doğrulanacak
