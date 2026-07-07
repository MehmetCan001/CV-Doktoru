# CHECKPOINT — 2026-07-07 — v1.7

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.
**URL:** https://cvdoktoru.com ✅ CANLI (FastAPI sürümü, polling mimarisiyle — bkz. checkpoint-son v1.6)

## Bu Oturumda Yapılanlar

### 1) SEO — Google'da hiç görünmüyordu, teknik altyapı kuruldu
- `templates/index.html`: meta description, keywords, canonical URL, Open Graph, Twitter Card, `WebApplication` JSON-LD eklendi.
- `src/server.py`: `GET /robots.txt` ve `GET /sitemap.xml` route'ları eklendi (`SITE_URL` env değişkeniyle, varsayılan `https://cvdoktoru.com`).
- Google Search Console: **Domain property** (`sc-domain:cvdoktoru.com`) doğrulandı — HTML meta tag yöntemiyle (`google-site-verification` içeriği `index.html`'e eklendi).
- Sitemap Search Console'a gönderildi ve **"Başarılı"** durumda (1 sayfa keşfedildi). URL Inspection ile ana sayfa için "Request Indexing" **henüz yapılmadı — sıradaki adım**.
- Google Ads: kullanıcı şu an bütçe ayırmıyor, ileri tarihe ertelendi.

### 2) Fake-door talep testi — 1-2 haftalık gözlem başladı
Kullanıcının amacı: 189 TL'lik bir premium özelliğe gerçek talep var mı, veriye dayalı karar vermek.

**Önemli düzeltme (dikkat — tekrar etmeyin):** İlk taslakta premium teklif "İK uzmanının CV'yi birebir incelediği 30 dk görüşme" olarak yazılmıştı. Kullanıcı **gerçek insanla çalışma planı olmadığını** açıkça belirtti — bu, test sonucu talep gösterse bile inşa edilemeyecek bir vaat olurdu (yanıltıcı fake-door). Teklif **"Derin Analiz Paketi"** olarak değiştirildi: LinkedIn optimizasyonu + maaş beklentisi analizi + ön yazı taslağı + genişletilmiş mülakat hazırlığı — hepsi mevcut AI motoruyla, insan gerektirmiyor. **Kural:** Fake-door kopyası her zaman gerçekten inşa edilebilecek/edilmesi planlanan bir şeyi test etmeli, aksi halde sinyal anlamsızlaşır.

**Mimari kararlar:**
- Ana ücretsiz "Analizi Başlat" CTA'sına **dokunulmadı** — kullanıcı bilinçli olarak "ayrı premium katman" yaklaşımını seçti (marka vaadi "kayıt yok, ödeme yok" korunuyor). Premium teklif farklı bir değer önerisi sunduğu için bu karar doğru.
- `src/analytics.py` (yeni): çerezsiz, sunucu-taraflı sayaç. IP'ler ham saklanmıyor, tuzlanmış hash tutuluyor (`ANALYTICS_SALT`). İki dosya: `data/analytics_events.jsonl` (append-only event log: `page_view`, `premium_click`) ve `data/leads.json` (e-posta listesi). İkisi de `.gitignore`'da (leads.json PII içeriyor).
- `src/server.py`: `POST /api/track/visit`, `POST /api/track/premium-click`, `POST /api/leads`, `GET /api/analytics/summary?key=...&days=14` eklendi. Summary endpoint `ANALYTICS_ADMIN_KEY` ile korunuyor, anahtar yoksa/yanlışsa her zaman 403.
- **Karar matrisi** `summary()` içinde otomatik hesaplanıyor: `unique_visitors < 30` → `YETERSİZ_VERİ`; tıklama oranı `< %1` → `KILL`; `%1–5` → `OPTIMIZE`; `> %5` → `GREEN_LIGHT`.
- `templates/index.html`: "Derin Analiz Paketi — 189 ₺" kartı, tıklayınca e-posta yakalama formu açılıyor ("ilk 100 kullanıcı, lansmanda %50 indirim" kancası).

**Sunucuda kurulu, kullanıcının .env'inde DEĞİL:**
```
ANALYTICS_ADMIN_KEY=9f6bea6d42c9dcc321f104424bdb85665e648db44664a7ee
```
Bu anahtar `/opt/cv-doktoru/.env` içinde (sadece sunucuda, repo'ya girmedi). Sonuçları görmek için:
`https://cvdoktoru.com/api/analytics/summary?key=9f6bea6d42c9dcc321f104424bdb85665e648db44664a7ee&days=14`

### 3) Deploy — iki kez yapıldı, ikisi de doğrulandı
- Deploy yöntemi: yerelde commit + `git push origin main` → sunucuda `ssh -i ~/.ssh/cv_doktoru root@46.225.20.111` → `cd /opt/cv-doktoru && git pull && systemctl restart cv-doktoru`.
- İlgili commit'ler: `d4682ae` (SEO + analytics altyapısı), `239bd54` (karar matrisi + 189 TL), `76f9568` (İK uzmanı metni kaldırıldı, Derin Analiz Paketi'ne çevrildi).
- Her deploy sonrası `curl` ile canlıda doğrulandı, `journalctl -u cv-doktoru` temiz.

## Açık Kalan Sorular / Sıradaki Adımlar
- [ ] Search Console → URL Inspection → ana sayfa için **Request Indexing** yapılmadı, kullanıcıya hatırlat.
- [ ] Bing Webmaster Tools'a import önerildi, yapılıp yapılmadığı bilinmiyor.
- [ ] **1-2 hafta sonra** (~2026-07-14 – 2026-07-21 civarı) `unique_visitors >= 30` olduğunda `verdict` alanına bakılıp go/no-go kararı verilecek — bu oturumun ana amacı, unutma.
- [ ] Google Ads bütçe ayrılınca ele alınacak (anahtar kelime + reklam metni taslağı hazır değil, istenirse hazırlanabilir).
- [ ] `data/analytics_events.jsonl` şu an sadece birkaç test isteği içeriyor (temizlenmedi) — gerçek ölçüm bugünden itibaren sayılmalı, ilk birkaç kaydı (test amaçlı curl istekleri) yorumlarken göz ardı et.

## Bilinen Riskler
- `_MIN_SAMPLE_SIZE = 30` sabit kodlanmış (`src/analytics.py`). Kullanıcı çok düşük trafik alırsa 1-2 haftada bu sayıya ulaşmayabilir — o durumda "YETERSİZ_VERİ" ile karşılaşır, süreyi uzatmak gerekebilir.
- Analytics dosyaları (`analytics_events.jsonl`, `leads.json`) tek sunucuda düz dosya olarak tutuluyor, yedeklenmiyor. Uzun vadede önemli değilse sorun değil (test verisi), ama leads.json'daki e-postalar iş değeri taşıyorsa sunucu yedeği düşünülmeli.
