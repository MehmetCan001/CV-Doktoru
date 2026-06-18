# CHECKPOINT — 2026-06-17 — v0.8

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı. Kullanıcı CV + iş ilanı girer, mentor tarzı detaylı analiz raporu alır.

## Tech Stack
- **Frontend:** Streamlit (`src/app.py`)
- **AI Motoru:** Anthropic Claude (`src/analyzer.py`) — `claude-sonnet-4-6` aktif
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
- [x] **Claude API geçişi** — ANTHROPIC_API_KEY eklendi, Claude aktif ✅
- [x] **Streaming** — `_analyzer_claude.py`'de `analyze_stream()` eklendi; `app.py` streaming modunda çalışıyor
- [x] **Sahte istatistikler kaldırıldı** — "8.400+", "%73", "4.8★", "30 sn" yerine dürüst özellik rozetleri: Ücretsiz / Kayıt yok / Türkiye'ye özel / Claude 4 destekli
- [x] **Prompt düzeltmeleri (2026-06-17):**
  - LinkedIn özet: GitHub linki yokken "GitHub'da mevcut" yazma kuralı eklendi
  - SOMUT EYLEMLER: Lokasyon tutarsızlığı varsa mutlaka eylem maddesi ekle (max 6'ya çıktı)

## Mevcut Durum
- **Faz:** Geliştirme + test aşaması
- **Claude API:** Aktif, ANTHROPIC_API_KEY `.env`'de var ✅
- **Streaming:** Kod hazır, gerçek performans testi yapılmadı (yarın devam)
- **Çalıştırma:** `python -m streamlit run src/app.py` → http://localhost:8501
- **Analiz süresi:** ~60 saniye (streaming ile kullanıcı 2-3 sn'de ilk metni görüyor)

## Alınan Mimari Kararlar
1. **MAX_TOKENS = 16384** — truncation olmasın diye
2. **Few-shot: 2 örnek** — orta uyum (ornek_1) + yanlış sektör (ornek_2)
3. **Model-agnostik promptlar** — Gemini fallback hâlâ çalışıyor
4. **Streaming mimarisi:** `analyze_stream()` → `st.write_stream()` → `st.rerun()` → styled rapor
5. **Sahte metrik yasağı:** Hero'da uydurma sayı yok, sadece özellik rozetleri

## Açık Kalan / Yarın Yapılacaklar
1. **Streaming gerçek testi** — kullanıcı metin akışını görüyor mu kontrol et
2. **Süre sorunu** — toplam 60 sn gerçekten sorunsa seçenekler:
   - Token sayısını azalt (raporu kısalt)
   - claude-haiku-4-5 dene (çok daha hızlı, kalite düşer)
   - Kullanıcıya "~1 dakika" beklentisi ver
3. **Streamlit Cloud deploy** — `cvdoktoru.streamlit.app`
4. **Domain** — cvdoktoru.com.tr

## Bilinen Sorunlar
- Analiz ~60 saniye sürüyor (Claude Sonnet + uzun prompt + 16384 token)
- Streaming çalışıyor ama kullanıcı deneyimini yarın doğrula
