# CHECKPOINT — 2026-07-01 — v1.4

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.

## Tech Stack
- **Frontend/UI**: Streamlit (`src/app.py`)
- **AI Motoru**: Anthropic Claude (`src/_analyzer_claude.py`) — `claude-sonnet-4-6`
- **Dosya Okuma**: `src/pdf_reader.py` — PDF, DOCX, düz metin
- **Prompt Sistemi**: `src/prompt_loader.py`
- **Config**: `src/config.py` — MAX_TOKENS=32768, _TIMEOUT=300s
- **Prompt Dosyaları**: `prompts/` (system_prompt.md, analysis_prompt.md, examples/)
- **Bilgi Tabanı**: `knowledge/turk_is_kulturu.md`

## Tamamlanan Modüller
- [x] Temel CV + iş ilanı analizi
- [x] PDF/DOCX/metin dosyası okuma
- [x] Streamlit UI — hero, form, rapor gösterimi, PDF/TXT indirme
- [x] Prompt sistemi — system_prompt + few-shot + analysis_prompt
- [x] Tüm rapor bölümleri (13 bölüm)
- [x] Koşullu bölümler (ALTERNATİF HEDEFLER skor<30, MÜLAKAT HAZIRLIĞI skor≥40)
- [x] Claude API geçişi — ANTHROPIC_API_KEY ✅
- [x] Skor yuvarlama — `_round_score()` ile 5'e yuvarla
- [x] Premium SaaS UI redesign
- [x] MAX_TOKENS 32768
- [x] Streaming tamamen kaldırıldı → blocking mode
- [x] **Deploy: Hetzner CX23, Ubuntu 22.04** ✅ (2026-07-01)
- [x] **Domain: https://cvdoktoru.com** ✅ (GoDaddy)
- [x] **HTTPS: Let's Encrypt / Certbot** ✅
- [x] **Nginx reverse proxy** ✅
- [x] **Systemd servisi** ✅ (otomatik başlatma)

## Mevcut Durum
- **URL**: https://cvdoktoru.com ✅ CANLI
- **Sunucu**: Hetzner CX23, Nuremberg — IP: 46.225.20.111
- **Servis**: systemd `cv-doktoru.service` — otomatik restart aktif
- **SSL**: Let's Encrypt (certbot otomatik yeniler)
- **Analiz modu**: Blocking (`doctor.analyze()`) + `st.info()` placeholder + fall-through render

## Alınan Mimari Kararlar
1. **MAX_TOKENS = 32768** — Türkçe + detaylı format çıktıyı 10K-16K token'a çıkarıyor
2. **_TIMEOUT = 300s** — büyük promptlar 2-4 dk sürebilir
3. **Streaming YOK** — Streamlit'te yapısal olarak güvenilmez
4. **st.status() YOK** — blocking API çağrısında UI güncellemesi çalışmıyor
5. **st.rerun() YOK** — uzun API çağrısı sırasında WebSocket yenilenirse session_state boş gelir
6. **st.info() placeholder** — `_notice = st.info(...)` → `_notice.success(...)` güvenilir tek yol
7. **Fall-through rendering** — analiz biter bitmez aynı script akışında rapor render edilir
8. **Streamlit Cloud terk edildi** — blocking 2-4 dk çağrı Cloud'un script timeout'unu aşıyor
9. **Hetzner CX23 seçildi** — Railway/Render yerine VPS: uzun timeout sorunu çözüldü

## Güncelleme Prosedürü (deploy sonrası)
Kodda değişiklik olduğunda sunucuda:
```bash
cd /opt/cv-doktoru && git pull && systemctl restart cv-doktoru
```

## Sonraki Özellik Adayları
- [ ] LinkedIn profil önerisi bölümü (CVCIM + ResumeWorked'dan öğrenildi, talep kanıtlı)
- [ ] Yazım kalitesi boyutu (Grammarly'den ilham)
- [ ] Maaş beklentisi ipucu (Youthall verisi referans)
- [ ] Beta geri dönüşlerine göre prompt iyileştirme
- [ ] Firewall kuralları (Hetzner Firewall — sadece 80/443/22 aç)
- [ ] Hetzner otomatik backup aktifleştir

## Bilinen Sorunlar / Yapılmayanlar
- Hetzner Firewall henüz kurulmadı (sunucu şu an tüm portlara açık)
- Hetzner backup aktif değil
