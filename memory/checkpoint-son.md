# CHECKPOINT — 2026-07-10 — v1.9

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.
**URL:** https://cvdoktoru.com ✅ CANLI

## Bu Oturumda Yapılanlar

### 1) OG/Twitter paylaşım görseli
- `static/og-image.png` (1200×630) eklendi — `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` kaynağından piksel-tabanlı bbox tespitiyle (numpy threshold, arka plan gürültüsü temizlendi) wordmark lockup kırpılıp ölçeklendi.
- `templates/index.html`: `og:image`/`twitter:image` artık bu dosyaya işaret ediyor, `og:image:width/height` eklendi.
- Deploy edildi, canlıda `curl` ile doğrulandı.

### 2) Sayfa tasarım/fonksiyon geliştirme — 5 adımlık plan onaylandı, sırayla uygulanıyor
Kullanıcı: "her ikisi de" (tasarım + fonksiyon basit duruyor) dedi, 5 maddelik öncelik listesi sunuldu ve onaylandı. Kural: **her seferinde sadece 1 adım**, kullanıcı "devam" diyince sıradakine geçilecek.

**Sıra:**
1. ✅ **Örnek Analiz önizleme kartı** — tamamlandı, deploy edildi (commit `340f020`). `prompts/examples/ornek_1_yazilim.md`'deki kurgusal "Ahmet Yılmaz" örneğinden kısaltılmış demo: skor rozeti, 1 kırmızı bayrak, 1 güçlü nokta, alta soluklaşan fade + forma kaydıran CTA. Açıkça "ÖRNEK · DEMO" etiketli + "kurgusal CV" notu var (sahte testimonial değil).
2. ✅ **FAQ/güven bölümü** — tamamlandı, deploy edildi (commit `577825a`). Native `<details>/<summary>` akordiyon (JS'siz, klavye-erişilebilir), 5 soru: veri saklama, ücretsizlik+günlük 3 analiz limiti (`src/rate_limiter.py DAILY_LIMIT=3`'ten teyitli), süre (2-3 dk), dosya formatları (PDF/DOCX/metin, 10 MB), insan mı AI mı. "Neden Farklı" ile "Derin Analiz Paketi" kartları arasına yerleşti.
3. ⏳ **SIRADAKİ: Masaüstünde iki sütunlu/asimetrik hero düzeni** — henüz başlanmadı.
4. ⏳ Mikro-etkileşim/scroll animasyonları + mobilde sticky CTA bar — henüz başlanmadı.
5. ⏳ Sahte testimonial **eklenmeyecek** (gerçek kullanıcı verisi yok, karar zaten alındı — bu madde "yapılacak" değil, bilinçli "yapılmayacak" kararı).

**Yerel test yöntemi (bu oturumda kuruldu, tekrar kullanılabilir):**
```
cd cv-doktoru
"./venv/Scripts/python.exe" -m uvicorn src.server:app --host 127.0.0.1 --port 85XX
"/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu --no-sandbox --screenshot="<yol>.png" --window-size=1280,3000 "http://127.0.0.1:85XX/"
```
Not: proje kökünde iki farklı venv var — `venv/` (fastapi kurulu, ÇALIŞAN budur) ve `source/` (fastapi YOK, kullanma). Test bitince `netstat -ano | grep <port>` ile PID bulup `powershell -Command "Stop-Process -Id <pid> -Force"` ile kapat.

### 3) Fake-door analytics sorgusu — IP filtreleme yok
Kullanıcı `/api/analytics/summary` sonucunu paylaştı (18/30 tekil ziyaretçi, YETERSİZ_VERİ — normal, pencere henüz dolmadı). Soru: kendi IP'si sayıma dahil mi?
- **Cevap: Evet, dahil.** `src/analytics.py`'de hiçbir IP hariç tutma mantığı yok. Sayaç `gün:ip_hash` anahtarıyla tekilleştiriyor — aynı gün tekrar ziyaret tek sayılır, ama **farklı günlerde** ziyaret her seferinde ayrı "tekil ziyaretçi" sayılır. Kullanıcının deploy sonrası doğrulama ziyaretleri muhtemelen 18'in içinde, gerçek dış trafiği şişiriyor.
- **Açık öneri (henüz uygulanmadı, kullanıcı onaylamadı):** Ortam değişkeninde kendi IP hash'ini tanımlayıp `summary()`'de eleyen basit bir filtre eklenebilir. İstenirse yarın yapılabilir.

## Açık Kalan Sorular / Sıradaki Adımlar
- [ ] **Öncelik:** 5 adımlık tasarım planının 3. maddesi (masaüstü iki sütunlu hero) — kullanıcı "devam" dediğinde başla.
- [ ] Kendi IP'yi analytics sayımından hariç tutma filtresi (kullanıcı sordu ama henüz "yap" demedi — önce sor).
- [ ] Fake-door testi sonucu (`unique_visitors >= 30` olunca `/api/analytics/summary` verdict) hâlâ değerlendirilmedi — 2026-07-07'de başladı, hacim düşük (3 günde 18), ~2026-07-14/21 civarı tekrar bakılacaktı ama bu tempoyla daha uzun sürebilir.
- [ ] Search Console → URL Inspection → "Request Indexing" hâlâ yapılmadı (önceki checkpoint'ten devralındı, hâlâ açık).

## Bilinen Riskler / Dosya Notları
- Proje kökünde `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` ve `Logo.png` hâlâ commit edilmemiş kaynak dosyalar olarak duruyor (`static/og-image.png` ve `static/logo.png` bunlardan türetildi). Silinmediler, kullanıcının kendi dosyaları — dokunma.
- İki venv karışıklığı (`venv/` vs `source/`) — yukarıda not edildi, ileride tekrar kafa karıştırabilir.
