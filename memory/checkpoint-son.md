# CHECKPOINT — 2026-07-02 — v1.6

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.
**URL:** https://cvdoktoru.com ✅ CANLI (şu an hâlâ Streamlit sürümü)

## Tech Stack (Mevcut — Canlıda)
- **Frontend/UI**: Streamlit (`src/app.py`) — YEREL FASTAPI SÜRÜMÜ HAZIR, DEPLOY EDİLMEDİ
- **AI Motoru**: Anthropic Claude (`src/_analyzer_claude.py`) — `claude-sonnet-4-6`
- **Sunucu**: Hetzner CX23, Nuremberg — IP: 46.225.20.111
- **Servis**: systemd `cv-doktoru.service` (hâlâ Streamlit'i çalıştırıyor)
- **Reverse proxy**: Nginx + Let's Encrypt HTTPS
- **Domain**: GoDaddy `cvdoktoru.com`

## FastAPI Geçişi — DURUM: Yerelde tamamlandı, deploy bekliyor
Bu oturumda (2026-07-02) yapıldı:
- [x] `src/server.py` — FastAPI app. Endpoint'ler:
  - `GET /` → `templates/index.html`
  - `GET /api/remaining` → kalan günlük hak
  - `POST /api/analyze` → multipart form (cv_file veya cv_text + job_text), blocking analiz (SSE/streaming KULLANILMADI — bilinçli karar, aşağıya bak)
  - `POST /api/pdf` → rapor metninden PDF üretir
- [x] `templates/index.html` — Streamlit tasarımının vanilla HTML/CSS/JS portu (hero, adımlar, form, loading animasyonu, rapor gösterimi, indirme butonları)
- [x] `src/pdf_export.py` — PDF üretimi `app.py`'den ayrıştırıldı, hem Streamlit hem FastAPI kullanıyor (kod tekrarı yok)
- [x] `src/rate_limiter.py` — `get_client_ip_from_headers()` eklendi (generic, hem Streamlit hem FastAPI request.headers ile çalışır); eski `get_client_ip()` Streamlit için korundu
- [x] `requirements.txt` — fastapi, uvicorn[standard], python-multipart eklendi
- [x] Lokalde uçtan uca test edildi: gerçek Claude API çağrısı ile analiz (200 OK, 2 dk sürdü), PDF export (6 sayfa, geçerli PDF), rate limiter (3→2 azaldı), Streamlit app.py hâlâ syntax-valid ve yeni pdf_export'u kullanıyor

### Bilinçli karar: Gerçek SSE token-streaming YOK
Checkpoint v1.5'te "SSE ile token token akış" hedeflenmişti. Kullanıcıyla görüşüldü:
`_analyzer_claude.py`'deki `analyze_stream()` metodu bozuktu (`self.client` hiç tanımlanmamış,
çağrılsa `AttributeError` verirdi). Gerçek streaming hem bu metodun düzeltilmesini hem yeni bir
SSE yüzeyini gerektiriyordu — ekstra risk. Bunun yerine **blocking + sahte ilerleme çubuğu**
(mevcut Streamlit UX'inin birebir aynısı) seçildi. `doctor.analyze()` FastAPI'de
`run_in_threadpool` ile çalıştırılıyor. İleride gerçek streaming istenirse önce
`analyze_stream()` düzeltilmeli.

### XSS önlemi — rapor gösterimi
Rapor metni LLM çıktısı olduğu için (kullanıcı girdisi + prompt injection riski var),
`templates/index.html` içinde üçüncü parti markdown kütüphanesi (marked.js vb.) YERİNE
bağımlılıksız, önce tüm metni escape edip sonra sınırlı regex kalıpları uygulayan bir
JS fonksiyonu yazıldı (`renderMarkdown`). Böylece raw HTML/script LLM çıktısına sızsa bile
tarayıcı tarafından hiçbir zaman kod olarak yorumlanmaz. Ayrıca SRI hash tahmini / CDN
tedarik zinciri riski de ortadan kalktı.

## DEPLOY TAMAMLANDI — 2026-07-02 16:55 UTC
FastAPI sürümü **canlıya alındı**. `cvdoktoru.com` artık `src/server.py`'yi çalıştırıyor.
- SSH erişimi: `~/.ssh/cv_doktoru` anahtarıyla `root@46.225.20.111` (Windows'ta ~/.ssh içinde zaten mevcuttu)
- Sunucuda proje: `/opt/cv-doktoru` (git ile yönetiliyor, origin: github.com/MehmetCan001/CV-Doktoru)
- systemd: `/etc/systemd/system/cv-doktoru.service` → `ExecStart=uvicorn src.server:app --host 127.0.0.1 --port 8501`
- Eski Streamlit servis dosyası yedeği: `/etc/systemd/system/cv-doktoru.service.streamlit-backup-20260702` (rollback gerekirse bu dosyayı `cv-doktoru.service` üzerine kopyalayıp `daemon-reload && restart` yeterli)
- Nginx'e dokunulmadı (zaten 127.0.0.1:8501'e proxy yapıyordu)
- Doğrulama: `https://cvdoktoru.com/` (200), `/api/remaining` (200), gerçek `/api/analyze` isteği HTTPS üzerinden uçtan uca test edildi (200, tam rapor)
- Nginx/journalctl logları temiz, hata yok

## KRİTİK FIX — 2026-07-02 17:19 UTC — Polling mimarisine geçiş
Deploy sonrası canlıda gerçek kullanıcı testi yapıldı: mobil sorunsuz çalıştı ama **PC
tarayıcısında `net::ERR_CONNECTION_RESET`** hatası alındı (DevTools Console ile doğrulandı).
Sunucu tarafı log analizi: PC'nin isteği aslında sunucuda 200 OK ile tamamlanmıştı (bir
önceki denemede), ama ikinci denemede istek **nginx'e hiç ulaşmadı** — bağlantı client
tarafında/ağ yolunda kesildi.

**Kök sebep:** `/api/analyze` isteği 2-4 dakika boyunca tek bir HTTP bağlantısını hiç veri
akışı olmadan açık tutuyordu. Bazı ev/kurumsal ağların NAT/firewall'ı bu "boşta" bağlantıyı
ölü sayıp RST ile kesiyor. Mobil şebekede bu sorun yaşanmadı (muhtemelen farklı NAT zaman
aşımı). **Bu, Streamlit'i terk etmemize sebep olan "uzun bağlantı kırılganlığı" sorununun
aynısı — sadece taşıma katmanı (WebSocket → düz HTTP) değişmişti, temel risk değişmemişti.**

**Çözüm — iş kuyruğu + polling:**
- `POST /api/analyze/start` — artık < 1sn içinde `job_id` döner, analiz arka planda
  `threading.Thread` ile yürütülür. Sonuç bellekte `_jobs` sözlüğünde tutulur (30 dk TTL,
  her yeni job'da eskiler temizlenir — tek process olduğu için Redis vb. gerekmedi).
- `GET /api/analyze/status/{job_id}` — tarayıcı 3 saniyede bir sorgular, her istek çok
  kısa sürdüğü için hiçbir NAT/firewall'ın kesecek "boşta bağlantı"sı olmuyor.
- `templates/index.html` — `pollJobStatus()` fonksiyonu eklendi, max 10 dk polling sınırı var.
- Hem lokalde hem canlıda (`cvdoktoru.com` üzerinden gerçek HTTPS isteğiyle) uçtan uca
  doğrulandı — çalışıyor.

**KURAL (CLAUDE.md'ye de eklenmeli — bir sonraki oturumda hatırlat):** Bu projede LLM
çağrıları 2-4 dakika sürüyor. Tarayıcı ↔ sunucu arasında **tek bir bağlantının bu süre
boyunca veri akışı olmadan açık kalmasına asla güvenme** — WebSocket'te de, düz HTTP'de de
aynı NAT/firewall/idle-timeout riski var. Doğru desen: iş başlat (hızlı yanıt) + kısa
aralıklarla durum sorgula (polling) ya da düzenli heartbeat ile canlı tut (SSE + ping).

## Yapılmayanlar / Sıradaki
- [ ] Mobil cihazdan gerçek dosya yükleme testi (henüz ayrıca doğrulanmadı, ama polling akışı mobilde de aynı şekilde çalışır)
- [ ] Sorunsuz birkaç gün geçince: `src/app.py`, `.streamlit/` klasörü ve `streamlit` bağımlılığını kaldır (şu an ölü kod, ama güvenlik ağı olarak bırakıldı)
- [ ] `.streamlit/config.toml`'daki sunucu-lokal elle yapılmış değişiklik (`port=8501`, `enableXsrfProtection=false`) artık kullanılmıyor, temizlik sırasında kaldırılabilir

## Analiz Kodu (Dokunulmadı — Plan Buydu, Uygulandı)
- `src/analyzer.py`, `src/_analyzer_claude.py`, `src/prompt_loader.py`, `src/pdf_reader.py`
- `src/rate_limiter.py` — sadece IP çıkarma fonksiyonu genelleştirildi, iş mantığı (check_and_increment, remaining_today) değişmedi
- `prompts/`, `knowledge/` — dokunulmadı

## Bilinen Sorunlar / Riskler
- FastAPI sürümü henüz production'da DEĞİL — sadece yerel makinede doğrulandı
- Mobil dosya yükleme yeni HTML/JS ile henüz gerçek bir mobil cihazda test edilmedi
- `data/last_report.txt` mekanizması FastAPI sürümünde de korundu (kurtarma amaçlı), ama artık session_state sorunu olmadığı için gereksiz — istenirse kaldırılabilir
