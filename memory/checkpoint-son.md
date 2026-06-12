# CHECKPOINT — 2026-06-11 — v0.7

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı. Kullanıcı CV + iş ilanı girer, mentor tarzı detaylı analiz raporu alır.

## Tech Stack
- **Frontend:** Streamlit (`src/app.py`)
- **AI Motoru:** Anthropic Claude (`src/analyzer.py`) — `claude-sonnet-4-6` (API key gelince aktif)
- **Dosya Okuma:** `src/pdf_reader.py` — PDF, DOCX, düz metin
- **Prompt Sistemi:** `src/prompt_loader.py`
- **Config:** `src/config.py` — MAX_TOKENS=16384
- **Prompt Dosyaları:** `prompts/` (system_prompt.md, analysis_prompt.md, examples/)
- **Bilgi Tabanı:** `knowledge/turk_is_kulturu.md`

## Tamamlanan Modüller
- [x] Temel CV + iş ilanı analizi (Gemini API)
- [x] PDF/DOCX/metin dosyası okuma
- [x] Streamlit UI — hero, form, rapor gösterimi, PDF/TXT indirme
- [x] Prompt sistemi — system_prompt + few-shot + analysis_prompt
- [x] KIRMIZI BAYRAKLAR, GÜÇLÜ NOKTALAR, İŞ İLANINA UYUM bölümleri
- [x] ALTERNATİF HEDEFLER (skor < 30)
- [x] MÜLAKAT HAZIRLIĞI (skor ≥ 40) — 5 soru + neden soruluyor
- [x] ATS Uyumluluk Notu
- [x] Lokasyon çelişkisi + doğum tarihi ön kontrolleri
- [x] SON SÖZ anti-pattern kuralları
- [x] GÜÇLÜ NOKTALAR "öne çıkarmak için" zorunluluğu + **format** (bold "Öne çıkarmak için:" satırı zorunlu)
- [x] Köşeli parantez fix (staj bilgisi yoksa tahmin + dipnot)
- [x] Loading adım mesajları (st.status — 4 adım + tamamlandı/hata durumu)
- [x] Few-shot örnek 2 (yanlış sektör senaryosu)
- [x] CLAUDE.md — proje bağlamı, rakip analizi, stratejik mesajlar
- [x] **LinkedIn Profil Önerisi bölümü**
- [x] **Maaş Beklentisi İpucu bölümü** — koşulsuz, Youthall uyarılı, yanlış sektör vakasına özgü ton
- [x] **temperature=0** — skor tutarsızlığı fix (`src/analyzer.py`) (ORTA VADELİ ile MÜLAKAT HAZIRLIĞI arasında, koşulsuz)
- [x] **Claude API geçişi** — fallback mimarisi: `ANTHROPIC_API_KEY` varsa Claude, yoksa Gemini (`_analyzer_claude.py` + `_analyzer_gemini.py`)
- [x] **Gemini skor tutarsızlığı fix** — `thinking_budget=0` (Gemini 2.5 thinking süreci temperature=0'ı geçersiz kılıyordu)
- [x] **Gemini 503 retry** — 3 deneme, 5s/10s bekleme, kullanıcıya anlamlı hata mesajı
- [x] **Yazım Kalitesi bölümü** — pasif cümle + klişe tespiti, KIRMIZI BAYRAKLAR'dan sonra, her iki örneğe de eklendi
- [x] **Yazım Kalitesi köşeli parantez fix** — `[belirli bir alanda]`/`[varsa...]` placeholder'ları yasak kuralı eklendi; Türkçe pasif tanımı netleştirildi (tarafından+edildi kalıbı); max 3→2 örnek; örnek rewrite'lardaki `[proje dersi]`/`[proje konusu]` somutlaştırıldı
- [x] **LinkedIn Özet köşeli parantez fix** — `analysis_prompt.md`'ye "bu taslakta `[...]` kullanma" kuralı eklendi; `ornek_1`'deki `[teknoloji]` → `Python` somutlaştırıldı; re-test geçti ✅
  - Başlık (Headline) önerisi — recruiter arama formatı
  - Özet (About) taslağı — CV'den gerçek verilerle
  - Beceriler listesi — koşullu ifade yasak ("eğer biliyorsan" tipi)

## Mevcut Durum
- **Faz:** Geliştirme devam ediyor — localhost'ta çalışıyor
- **Son test:** LinkedIn bölümü gerçek CV+ilan ile test edildi, doğru çıktı ✅
- **Claude API:** Kod hazır, `.env`'e `ANTHROPIC_API_KEY` yazılınca aktif olur (15 Haziran)
- **Çalıştırma:** `python -m streamlit run src/app.py` → http://localhost:8501

## Alınan Mimari Kararlar
1. **MAX_TOKENS = 16384** — 4096 ve 8192 truncation yapıyordu
2. **Few-shot: 2 örnek** — orta uyum (ornek_1) + yanlış sektör (ornek_2)
3. **Model-agnostik promptlar** — Gemini → Claude geçişinde prompt dosyaları değişmeyecek
4. **Koşullu bölümler** — "SADECE X KOŞULDA EKLE" pattern'i çalışıyor
5. **st.status()** — st.spinner() yerine adım adım loading (Streamlit 1.27+)
6. **GÜÇLÜ NOKTALAR formatı** — Her madde: açıklama + zorunlu `**Öne çıkarmak için:**` satırı

## Prompt Öğrenmeleri (Bu Oturumdan)
- **LinkedIn Skills koşullu ifade tuzağı**: Model "Git (eğer kullanıyorsan)" gibi koşullu ifade yazabilir. Çözüm: prompt'a açık yasak + örneklerde düz liste.
- **GÜÇLÜ NOKTALAR format kayması**: Kural var ama format örneği yoksa model gömülü metin yazıyor, "Öne çıkarmak için:" satırını atlıyor. Çözüm: prompt'a bold format + örneklere satır eklendi.
- **LinkedIn bölümü CV verilerini kullanıyor**: Başlık, özet ve beceriler CV'deki gerçek verilere dayandı — jenerik değil. ✅

## Açık Kalan Sorular / Sonraki Adımlar
### 2026-06-12 — Yapılacaklar Listesi
1. ~~**Yazım Kalitesi re-test**~~ ✅ TAMAMLANDI — sıfır bracket, pasif mis-sınıflandırma yok, klişe tespiti doğru
2. **Deploy hazırlığı (Streamlit Cloud)** — `secrets.toml` şablonu, `.gitignore` kontrolü, GitHub'a ilk push
3. **15 Haziran hazırlığı** — `.env`'e `ANTHROPIC_API_KEY` ekle, `analyzer.py` Claude branch'e geçiyor mu test et

### Öncelikli (Ayın 15'inde bütçe gelince)
1. ~~**Claude API'ye geç**~~ ✅ KOD HAZIR — `.env`'e `ANTHROPIC_API_KEY` yaz, bitti
2. **Streamlit Cloud'a deploy** — `cvdoktoru.streamlit.app` veya custom domain
3. **Domain al** — cvdoktoru.com.tr (~200-400 TL/yıl)

### Özellik Sırası (Prompt Seviyesi — Bütçesiz Yapılabilir)
1. ~~LinkedIn profil önerisi bölümü~~ ✅ TAMAMLANDI
2. ~~Maaş beklentisi ipucu~~ ✅ TAMAMLANDI
3. Yazım kalitesi boyutu (pasif cümle, klişe ifade tespiti)

### Orta Vadeli
- GitHub analizi (yazılımcılar için)
- B2B pilot (üniversite kariyer merkezi)
- API servisi (Bilsoft gibi şirketlere)

## Rakip Analizi Özeti (12 rakip)
**Küresel:** Adzuna, Zety, Grammarly, ResumeWorded, LoopCV
**Türk:** cvanaliz.com.tr, Anabasis.ai, anbean KAMPÜS, Youthall, CVCIM, Ono, Bilsoft

**Core mesaj (rakip analizinden kanıtlı):**
> "Şirketler artık CV'leri yapay zeka ile eliyor. Biz sana o yapay zekayı geçecek CV yazmayı öğretiyoruz."

## Bilinen Hatalar / Geçici Çözümler
- **Gemini 503 hatası**: Geçici yük sorunu. Tekrar deneyince geçer. Claude'a geçince olmayacak.

## Stratejik Notlar
- Bütçe yok şu an, ayın 15'ini bekliyoruz
- Deploy ve Claude API geçişi aynı anda yapılacak
- Rakip analizi tamamlandı, artık özellik geliştirmeye odaklanılıyor
- Gerçek kullanıcı testi henüz yapılmadı — deploy sonrası öncelik
