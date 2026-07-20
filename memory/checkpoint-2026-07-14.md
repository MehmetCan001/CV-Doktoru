# CHECKPOINT — 2026-07-14 — v1.10

## Proje Adı ve Amacı
**CV Doktoru** — Türkiye iş piyasasına özgü AI destekli CV analiz aracı.
**URL:** https://cvdoktoru.com ✅ CANLI

## Deploy Prosedürü (tekrar hatırlatma)
```
git add <dosyalar> && git commit -m "..." && git push origin main
ssh -i ~/.ssh/cv_doktoru root@46.225.20.111
cd /opt/cv-doktoru && git pull && systemctl restart cv-doktoru
```
Doğrulama: `curl -s https://cvdoktoru.com/ -o /tmp/live.html -w "%{http_code}\n"` + `grep` ile beklenen içeriği ara.

## Bu Oturumda Yapılanlar

### 1) Hero bölümü — masaüstünde iki sütunlu düzen ✅ DEPLOY EDİLDİ
5 adımlık tasarım planının 3. maddesi tamamlandı (commit `0ece33b`).
- `templates/index.html`: ≥900px'te `.hero-inner` grid'e geçiyor — solda `.hero-text` (mevcut başlık/alt metin/rozetler), sağda `.hero-visual` (dekoratif "87/100 Uyum Skoru" önizleme kartı, `aria-hidden="true"`, gerçek veri değil).
- <900px'te eski tek-sütunlu, ortalanmış görünüm aynen korunuyor, `.hero-visual` gizli.
- Canlıda `curl` + local headless Chrome screenshot ile doğrulandı.

**Yöntemsel not (önemli, tekrar karşılaşılabilir):** Headless Chrome'da `--window-size=390,900` gibi bir CLI bayrağı **gerçek bir 390px mobil viewport oluşturmuyor** — tarayıcı gerçekte ~504px genişliğinde render edip görüntüyü istenen boyuta kırpıyor. Bu yüzden ilk testte yanlışlıkla bir "mobil taşma hatası" tespit ettim, gereksiz bir CSS "düzeltmesi" ekledim, sonra CDP `Emulation.setDeviceMetricsOverride` ile gerçek 390px viewport'ta test edince hatanın olmadığını gördüm ve gereksiz değişikliği geri aldım. **Kural:** Mobil genişlik testi için `--window-size` yetmez, CDP üzerinden `Emulation.setDeviceMetricsOverride` (width/height/deviceScaleFactor/mobile:true) kullanılmalı — yoksa yanlış pozitif/negatif sonuç alınır.

### 2) "Rapor Neye Benziyor" + SSS bölümleri sayfanın en altına taşındı ✅ DEPLOY EDİLDİ
Aynı commit (`0ece33b`), kullanıcı isteğiyle.
- Eski sıra: 3 Adım → Örnek Analiz (demo-card) → Neden Farklı → SSS → Derin Analiz Paketi → Form → ...
- Yeni sıra: 3 Adım → Neden Farklı → Derin Analiz Paketi → Form → Trust bar → (rapor alanı) → **Örnek Analiz** → **SSS** → footer.
- Mantık: ana dönüşüm akışı (adımlar → güven → form) öne alındı, açıklayıcı/destekleyici içerik (örnek rapor, SSS) sona kaydı.
- Canlıda `curl` ile bölüm sırası teyit edildi.

### 3) Deneyim süresi ↔ CV içi tarih tutarlılığı ön kontrolü — ⏳ EKLENDİ AMA TEST/DEPLOY EDİLMEDİ
Kullanıcının komutanı bir gözlem paylaştı: "CV'ye 5 yıl deneyim yazsam ama gerçekte 1 yılım olsa, yapay zeka bunu bilemez ki." Bu doğru ve önemli bir ürün sınırı.

**Yapılan ayrım:**
- Model, CV'de doğrulanamayan bağımsız bir iddiayı (tarih/iş geçmişi verilmemiş "5 yıl deneyim") **asla** sorgulayamaz/yalan işaretleyemez — bu referans kontrolü/mülakatın işi.
- Ama model, CV'nin **kendi içindeki hesaplanabilir çelişkiyi** yakalayabilir: "5 yıl deneyim" yazıp iş geçmişi tarihleri (örn. 2023-2024) toplamda 1 yılı gösteriyorsa, bu iç tutarsızlıktır.

**Değişiklik:** `prompts/analysis_prompt.md`'nin ön kontroller listesine yeni madde eklendi — hem tutarsızlık tespit talimatı hem de "sınır" uyarısı (doğrulanamayan iddialarda sessiz kal) aynı maddede birlikte. `CLAUDE.md` Bölüm 12 (prompt öğrenmeleri) ve Bölüm 14 (roadmap) güncellendi.

**Durum:** Diskte duruyor, **commit edilmedi, deploy edilmedi**. Proje kuralı gereği (Bölüm 15: Prompt Değişikliklerinde Test Protokolü) gerçek bir CV + ilanla test edilmeden deploy edilmemeli — bu gerçek bir Claude API çağrısı gerektiriyor. Kullanıcı "yarın devam edelim" dedi.

## Açık Kalan Sorular / Sıradaki Adımlar
- [ ] **Öncelik:** Deneyim süresi ↔ tarih tutarlılığı ön kontrolünü gerçek bir test CV'siyle doğrula (kasıtlı çelişki: "5 yıl deneyim" + 1 yıllık iş geçmişi tarihleri), sonra commit + deploy et. Ayrıca doğrulanamayan bağımsız iddiaların (tarihsiz "X yıl deneyim") yanlışlıkla sorgulanmadığını da kontrol et.
- [ ] 5 adımlık tasarım planının 4. maddesi — mikro-etkileşim/scroll animasyonları + mobilde sticky CTA bar — henüz başlanmadı.
- [ ] Kendi IP'yi analytics sayımından hariç tutma filtresi (önceki checkpoint'ten devralındı, kullanıcı henüz "yap" demedi).
- [ ] Fake-door testi sonucu (`unique_visitors >= 30` olunca `/api/analytics/summary` verdict) hâlâ değerlendirilmedi.
- [ ] Search Console → URL Inspection → "Request Indexing" hâlâ yapılmadı.

## Bilinen Riskler / Dosya Notları
- Proje kökünde `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` ve `Logo.png` hâlâ commit edilmemiş kaynak dosyalar olarak duruyor — dokunma, kullanıcının kendi dosyaları.
- İki venv karışıklığı (`venv/` vs `source/`) — `venv/` çalışan, `source/`'da fastapi yok, kullanma.
- Yerel test yöntemi: `"./venv/Scripts/python.exe" -m uvicorn src.server:app --host 127.0.0.1 --port 85XX` + headless Chrome. Mobil genişlik testi için CDP `Emulation.setDeviceMetricsOverride` kullan (yukarıya bkz, `--window-size` tek başına yeterli değil).
