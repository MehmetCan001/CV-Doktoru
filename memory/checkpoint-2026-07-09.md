# CHECKPOINT — 2026-07-09 — v1.8

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.
**URL:** https://cvdoktoru.com ✅ CANLI

## Bu Oturumda Yapılanlar

### Marka logosu eklendi
- Birkaç el-çizimi SVG konsepti denendi (belge+steteskop, belge+steteskop+ok ucu vb.) — hepsi kullanıcı tarafından reddedildi, koordinat tahminiyle serbest çizim bu kalitede güvenilir sonuç vermiyor.
- Kullanıcı kendi ürettiği (Gemini ile oluşturulmuş) logo görselini verdi ve **"aynen kullan, yeniden çizme"** dedi.
- İki kaynak dosya kullanıcı tarafından proje köküne bırakıldı: `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` (geniş wordmark lockup) ve `Logo.png` (kare, ikon+wordmark alt alta).
- **Son karar:** Logo navbar'dan tamamen kaldırıldı (kullanıcı istedi), sadece **favicon** olarak kullanılıyor.
- `static/logo.png`: `Logo.png` kaynağından piksel analiziyle (PIL, arka plan diff + bbox tespiti) otomatik kırpıldı — sadece ikon (steteskop+belge+yükseliş oku), metin yok, kare beyaz tuval, 862×862px.
- `templates/index.html`: `<link rel="icon" type="image/png" href="/static/logo.png?v=2">` — `?v=2` cache-busting parametresi eklendi çünkü tarayıcı favicon önbelleği sayfa önbelleğinden ayrı ve normal sert yenilemeyle kırılmıyor.
- OG/Twitter paylaşım meta etiketleri de `static/logo.png`'ye işaret ediyor (şu an ikon-only kare görsel — geniş wordmark lockup değil, ileride sosyal paylaşım için ayrı bir banner görseli gerekebilir, **not edildi, henüz yapılmadı**).

### Deploy süreci (tekrar hatırlatma — önceki checkpoint'te de vardı ama atlandı)
```
git push origin main
ssh -i ~/.ssh/cv_doktoru root@46.225.20.111
cd /opt/cv-doktoru && git pull && systemctl restart cv-doktoru
```
Bu oturumda 3 kez bu döngü çalıştırıldı (logo entegrasyonu → kırpma düzeltmesi → navbar kaldırma + favicon cache-bust). Her seferinde `curl` ile canlıda doğrulandı.

**Önemli ders (memory'ye de kaydedildi — `feedback-checkpoint-first.md`):** Oturum başında checkpoint okunmadığı için kullanıcı "web sayfasında değişiklik yok" dediğinde deploy yöntemi bilinmiyormuş gibi davranıldı, oysa önceki checkpoint'te zaten yazılıydı. Bir daha tekrarlanmamalı.

## Açık Kalan Sorular / Sıradaki Adımlar
- [ ] Kullanıcı tarayıcı sekmesinde favicon'un güncellendiğini henüz teyit etmedi (sekme kapat/aç veya gizli pencere önerildi, sonucu bilinmiyor).
- [ ] Google arama sonuçlarındaki eski favicon — Google'ın kendi tarama zamanlamasına bağlı, bizim kontrolümüzde değil, zamanla düzelir.
- [ ] OG/Twitter paylaşım görseli şu an kare ikon-only logo — sosyal medyada paylaşılınca ideal görünmeyebilir (geniş banner değil). İstenirse `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` kaynağından ayrı bir OG-image (1200×630 civarı, wordmark dahil) üretilebilir.
- [ ] Fake-door testi sonucu (`unique_visitors >= 30` olunca `/api/analytics/summary` verdict) hâlâ değerlendirilmedi — önceki checkpoint'ten devralınan açık madde, ~2026-07-14/21 civarı bakılacaktı.
- [ ] Search Console → URL Inspection → "Request Indexing" hâlâ yapılmadı (önceki checkpoint'ten devralındı).

## Bilinen Riskler / Dosya Notları
- Proje kökünde `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` ve `Logo.png` duruyor — repoya commit edilmedi (sadece kaynak/ham dosyalar), `static/logo.png` bunlardan türetildi. Silinmediler, kullanıcının kendi dosyaları.
- `static/logo.png` artık PNG (SVG değil) — gelecekte tekrar SVG'ye geçiş istenirse bu görseli vektöre çevirmek (trace) gerekir, elle yeniden çizmek değil (kullanıcı bunu reddetti).
