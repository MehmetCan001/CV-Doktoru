# CHECKPOINT — 2026-06-23 — v1.0

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı. Kullanıcı CV + iş ilanı girer, mentor tarzı detaylı analiz raporu alır.

## Tech Stack
- **Frontend:** Streamlit (`src/app.py`)
- **AI Motoru:** Anthropic Claude (`src/_analyzer_claude.py`) — `claude-sonnet-4-6` aktif
- **Dosya Okuma:** `src/pdf_reader.py` — PDF, DOCX, düz metin
- **Prompt Sistemi:** `src/prompt_loader.py`
- **Config:** `src/config.py` — MAX_TOKENS=16384
- **Prompt Dosyaları:** `prompts/` (system_prompt.md, analysis_prompt.md, examples/)
- **Bilgi Tabanı:** `knowledge/turk_is_kulturu.md`

## Tamamlanan Modüller
- [x] Temel CV + iş ilanı analizi
- [x] PDF/DOCX/metin dosyası okuma
- [x] Streamlit UI — hero, form, rapor gösterimi, PDF/TXT indirme
- [x] Prompt sistemi — system_prompt + few-shot + analysis_prompt
- [x] Tüm rapor bölümleri (KIRMIZI BAYRAKLAR, GÜÇLÜ NOKTALAR, LinkedIn, Mülakat, Maaş vb.)
- [x] Koşullu bölümler (ALTERNATİF HEDEFLER skor<30, MÜLAKAT HAZIRLIĞI skor≥40)
- [x] Loading adım mesajları (st.status)
- [x] Claude API geçişi — ANTHROPIC_API_KEY ✅
- [x] Streamlit Cloud deploy — `cv-doktoru-9bhxd3b7yje7g2rctuaeal.streamlit.app`
- [x] Skor yuvarlama — `_round_score()` ile 5'e yuvarla
- [x] **Streaming analiz** — `st.write_stream()` ile rapor yazar yazılmaz ekranda akar (2026-06-23)
- [x] **Hero subtitle renk fix** — `<strong>` → `<span>` ile beyaz renk (2026-06-23)
- [x] **CLAUDE.md güncellendi** — Streamlit CSS tuzakları + sürekli öğrenme kuralları (2026-06-23)
- [x] Premium SaaS UI redesign (Inter font, navy/accent renk paleti, dot-pattern bg)

## Mevcut Durum
- **Faz:** Deploy + domain bağlama aşaması
- **Claude API:** Aktif ✅
- **Deploy:** Streamlit Cloud aktif ✅
- **Streaming:** Aktif — rapor ilk token'dan itibaren ekranda görünür
- **MAX_TOKENS:** 16384 (8192'de analizler kesiliyordu, geri alındı)
- **Son commit:** `539cae1` — CLAUDE.md sürekli öğrenme kuralı
- **Çalıştırma:** `python -m streamlit run src/app.py` → http://localhost:8501

## Alınan Mimari Kararlar
1. **MAX_TOKENS = 16384** — 8192'de analizler kesildi, 16384 tutuldu. Streaming ile bekleme sorunu çözüldü.
2. **Few-shot: 2 örnek** — orta uyum (ornek_1) + yanlış sektör (ornek_2)
3. **Model-agnostik promptlar** — Gemini fallback hâlâ çalışıyor
4. **Streaming:** `st.write_stream()` + blocking fallback (streaming koparsa otomatik devreye girer)
5. **Skor yuvarlama:** `_round_score()` — 5'e yuvarla
6. **Inline style için `<span>` kullan** — Streamlit'in global CSS'i `strong`/`h1` vb. semantic tag'lere `!important` uygular, inline style ezer

## Açık Kalan / Sonraki Adımlar
1. **Domain bağlama** — `cvdoktoru.com.tr` GoDaddy'den satın alındı (2026-06-23), hesapta henüz görünmüyor. Göründüğünde: GoDaddy DNS'e CNAME ekle → Streamlit Cloud dashboard'da custom domain ayarla.
2. **Yazım kalitesi bölümü iyileştirme** — few-shot örneklerde daha güçlü hale getirilebilir
3. **Mobil test** — 2 kolon layout mobilde test edilmedi
4. **Gerçek CV ile test** — kullanıcı kendi CV'siyle test yapmalı

## CLAUDE.md Güncel Kurallar (Bu Oturumda Eklendi)
- Streamlit'te semantic HTML tag + inline style çalışmaz → `<span>` kullan
- CSS değişikliği öncesi seçici zincirini izle, sonra yaz
- Edit tool öncesi Türkçe karakter içeren satırları grep ile doğrula
- Hatadan anında ders çık, CLAUDE.md'ye anında yaz
- Token tasarrufu zorunlu — root cause anlaşılmadan kod yazılmaz

## Bilinen Sorunlar
- Streamlit Cloud'da cold start: ilk açılışta ekstra gecikme olabilir
- Hero inline style zorunlu (Streamlit primaryColor CSS çakışması)
