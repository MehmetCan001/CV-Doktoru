# CHECKPOINT — 2026-07-20 — v1.11

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

### Deneyim süresi ↔ CV içi tarih tutarlılığı ön kontrolü — ✅ TEST EDİLDİ, DÜZELTİLDİ, DEPLOY EDİLDİ
Önceki oturumdan (2026-07-14) devralınan açık iş: `prompts/analysis_prompt.md`'ye eklenen yeni ön kontrol maddesi diskte duruyordu ama gerçek bir CV ile test edilmemişti.

**Test yöntemi:** `ANTHROPIC_API_KEY` `.env`'de mevcut olduğu için gerçek Claude API çağrısıyla 2 test senaryosu koşturuldu (script: scratchpad'te, kalıcı değil).

- **Senaryo A (gerçek çelişki):** "5 yıl deneyim" özet cümlesi + tek iş "2023-2024" (tam tarih var). **İlk denemede doğru çalıştı** — KIRMIZI BAYRAK doğru formatta eklendi, ilk izlenim/mülakat sorularına/son söze kadar tutarlı yansıdı.
- **Senaryo B (doğrulanamayan iddia):** "6 yıl deneyim" + tek iş listelenmiş ama tarihi hiç yazılmamış. **İlk 2 denemede kural ihlal edildi**: model bunu "iç tutarsızlık, güven kaybına yol açar" diye KIRMIZI BAYRAK'a ekledi — kuralın "doğrulanamayan bağımsız iddiayı sorgulama" sınırını çiğnedi.

**Kök sebep:** İlk yazılan istisna metni sadece "tarih/iş geçmişi hiç verilmemiş" durumunu kapsıyordu, "iş var ama tarihsiz" ara durumunu ayrı ele almıyordu.

**Düzeltme (2 adım):**
1. İstisna listesine "iş pozisyonu var ama tarihi yok → sorgulama, sadece Eksik bölümler'e tarih notu düş" maddesi eklendi. Tek başına yetmedi.
2. Kuralın metnine doğrudan bir **YANLIŞ/DOĞRU örnek çifti** gömüldü (ayrı few-shot dosyası değil, kuralın kendi cümlesinin içinde). Üçüncü denemede model artık tarihsiz pozisyonu nötr dille ("tarih eksik, iddia doğrulanamıyor") işaretliyor, suçlayıcı "tutarsızlık/güven kaybı" dili kullanmıyor.

**Genel ders (CLAUDE.md Bölüm 12'ye işlendi):** Bir kurala istisna eklerken istisnanın tüm ara durumlarını ayrı ayrı yaz — "hiç yok" ile "var ama eksik" farklıdır. Pasif kural tek başına yetmiyor; YANLIŞ/DOĞRU örnek çiftini kuralın kendi metnine gömmek ayrı bir few-shot dosyasından daha ucuz ve aynı derecede etkili.

**Durum:** `prompts/analysis_prompt.md` + `CLAUDE.md` değişiklikleri commit'lendi (`d778eb8`) ve sunucuya deploy edildi, canlıda `curl` ile doğrulandı (HTTP 200).

### Fake-door sonucu geldi — DEĞERLENDİRİLDİ, karar bekliyor
`/api/analytics/summary` (14 gün): `unique_visitors: 55, premium_click_visitors: 2, leads_captured: 0, click_rate_pct: 3.6, verdict: OPTIMIZE`.

**Değerlendirme:** n=55, 2 tıklama — istatistiksel olarak güven aralığı çok geniş (~%0-12), bu veri tek başına "tasarım kötü" ya da "teklif zayıf" sonucuna varmak için yeterli değil. Asıl darboğaz muhtemelen **trafik hacminin çok düşük olması** (14 günde 55 ziyaretçi).

**Kullanıcı ayrıca bağımsız bir gözlem paylaştı:** Sayfanın "tamamen AI ile yapılmış" bir vibe verdiğini, güven vermediğini düşünüyor. Canlı siteden headless Chrome screenshot alınıp incelendi (1440px desktop). Tespit edilen somut sorunlar:
- Koyu lacivert hero + mavi gradient blob + pill-badge + yuvarlak ikon kutucukları — 2025-2026 AI SaaS'ında aşırı kullanılmış, "şablon" olarak tanınan bir görsel dil.
- **Hiç insan/fotoğraf yok** — CV gibi kişisel/güven gerektiren bir belgeyi teslim etmesi istenen kullanıcı için güven açığı.
- "87/100 Uyum Skoru" hero kartı ve "Örnek Analiz" kutusu gerçek ürün ekran görüntüsü değil, stilize edilmiş div'ler — "prototip/mockup" hissi veriyor.

**Verilen tavsiye (henüz uygulanmadı, kullanıcı onayı bekleniyor):** Tam bir "senior frontend redesign"a girişmeden önce ucuz güven-sinyali denemeleri:
1. Sahte mockup kart yerine gerçek ürünün ekran görüntüsü/GIF'i.
2. Küçük bir "Bunu ben yaptım" bölümü + kullanıcının gerçek fotoğrafı (solo-founder samimiyeti).
3. Tipografi/spacing'de şablon izlerini kıran dokunuşlar (roadmap'teki mikro-animasyon maddesiyle birleşebilir).

Kullanıcı "yarın devam edelim" dedi, henüz hangi yönde ilerleneceğine (ucuz güven-sinyali denemeleri mi, kapsamlı redesign mi) karar verilmedi — **yarın ilk soru bu olmalı, tekrar sorulmalı çünkü henüz cevaplanmadı.**

## Bu Oturumda Yapılanlar (devam) — Ucuz Güven-Sinyali Denemeleri

Kullanıcı yön kararını verdi: **ucuz güven-sinyali denemeleri** (kapsamlı redesign değil).

1. **Tipografi/spacing şablon kırma dokunuşları** — `templates/index.html`: `hero-badge`/`demo-badge` dolgu-pill'den altı-çizili etikete döndü; `step-icon-box` gradient lacivert kutudan beyaz+ince kontur (outline) stiline geçti; hero `accent` vurgusu italik oldu. Yerelde önce/sonra screenshot ile doğrulandı.
2. **Sahte mockup → gerçek ekran görüntüsü** — Kullanıcı gerçek bir analiz raporunun ekran görüntüsünü paylaştı. **Önemli güvenlik notu:** İlk 3 paylaşılan görüntüden biri kullanıcının gerçek Word CV dosyasıydı (isim, telefon, e-posta, doğum tarihi, adres açıkça görünüyordu) — kullanıma **kesinlikle uygun değildi**, kullanıcıya bu net şekilde işaretlendi ve kullanıcı o dosyaları silip temiz, sadece rapor kartını gösteren tek bir kırpılmış görüntü yükledi. O görüntüden `static/hero-rapor-onizleme.png` (üst 400px, başlık+skor+ilk paragraf) türetildi, hero'daki sahte "87/100" mockup kartının yerine kondu (fade efekti + "Gerçek bir analiz raporundan görüntü" altyazısıyla).
3. **Commit + deploy edildi:** `cd112d8`, push edildi, sunucuda `git pull` + `systemctl restart cv-doktoru`, canlıda `curl` ile doğrulandı (ana sayfa HTTP 200, `/static/hero-rapor-onizleme.png` HTTP 200).

**Bağımsız bulgu (bug, henüz düzeltilmedi):** Mobilde (390px genişlik test edildi) hero bölümündeki başlık/rozet metinleri sağdan taşıp kesiliyor. `git stash` ile değişikliklerden önceki haliyle de test edildi — **bu benim değişikliklerimden önce de vardı**, önceden var olan bir responsive bug. Kullanıcı "sonra bakarız" dedi, düzeltilmedi.

**Henüz yapılmayan (kullanıcıdan asset bekliyor):** "Bunu ben yaptım" güven bölümü — kullanıcının gerçek fotoğrafını sağlayacağı zaman eklenecek.

### 3 İlham Tasarımı Geldi ve Analiz Edildi (henüz uygulanmadı)
Kullanıcı 3 URL paylaştı: `easy.tools`, `supliful.com`, `cvcim.com`. Headless Chrome ile ekran görüntüleri alınıp incelendi (scratchpad'te, kalıcı değil). Ortak kalıplar:
1. **Üstte sosyal kanıt şeridi** — avatar kümesi + yıldız puanı (Easytools: "4.6/5.0 Trustpilot", Supliful: "1,500+ actively selling brands"), başlıktan önce.
2. **Gerçek ürün ekran görüntüsü hero'da** (Easytools) — bunu zaten bu oturumda uyguladık (`hero-rapor-onizleme.png`), yön doğrulandı.
3. **İsimli/rollü gerçek müşteri yorumları** (CVCIM: "Serdar Ç. — Endüstri Mühendisi" + alıntı) — jenerik yıldızlı yorumdan çok daha güçlü.
4. **Rozet/sertifika şeridi** (Supliful: FDA/cGMP/USA ikonlu rozetler) — bizim mevcut `trust-bar`'ın somutlaştırılmış versiyonu.
5. **Full-bleed gerçek/insan fotoğrafı arka planda** (CVCIM) — önceki oturumda tespit edilen "hiç insan yok" eksikliğine karşılık geliyor.

**Kritik dürüstlük sınırı (kullanıcıya iletildi):** Bu 3 sitenin en güçlü unsurları (isimli yorumlar, büyük sayılar — "$64M+", "1.6M+ sipariş") gerçek veriye dayanıyor. CV Doktoru'da henüz ne gerçek isimli kullanıcı yorumu var ne de büyük sayılar (14 günde 55 ziyaretçi) — CLAUDE.md dürüstlük ilkesi gereği bunlar sahte üretilemez.

**Kullanıcıya 4 öncelik seçeneği sunuldu** (rozet şeridi / hero foto / sosyal kanıt şeridi / sadece not al) — kullanıcı **rozet şeridi**ni seçti.

## Bu Oturumda Yapılanlar (devam) — Rozet Şeridi Eklendi

`templates/index.html`'e hero'nun hemen altına, "3 Adımda Sonuç" kartından önce yeni bir `section-card` içinde `badge-strip` eklendi: 4 dürüst güven rozeti — 🔒 SSL Şifreleme, 🗑️ Veri Saklanmaz, 🧠 Anthropic Claude API, 🇹🇷 Türk İş Kültürü Odaklı. Görsel dil, önceki oturumda kurulan `step-icon-box` outline stiliyle tutarlı (beyaz kart + ince kontur), sahte istatistik/sertifika iddiası yok. Mevcut alttaki `trust-bar` (form altı, düz metin pill) dokunulmadan kaldı — ayrı, daha hafif bir tekrar.

Yerelde `uvicorn` ile çalıştırılıp headless Chrome screenshot ile hem 1440px hem 390px genişlikte doğrulandı: masaüstünde 4 rozet tek satırda, mobilde 2x2 wrap düzgün çalışıyor. Bilinen hero taşma bug'ı (başlık/rozet metinleri 390px'te sağdan kesiliyor) bu değişiklikle ilgisiz, önceden vardı, hâlâ düzeltilmedi.

Commit + deploy edildi (bkz. commit hash için `git log`).

## Bu Oturumda Yapılanlar (devam) — Kapsamlı Yapısal Redesign

Kullanıcı rozet şeridini "öncekilerden hiçbir farkı yok, estetik değil" diye eleştirdi ve 3 ilham sitesiyle (easy.tools, supliful.com, cvcim.com) somut bir karşılaştırma istedi. 4 sayfa da (bizimki dahil) headless Chrome ile ekran görüntüsü alınıp yan yana incelendi. Somut fark: bizim sayfa koyu lacivert hero + art arda dizilmiş border/gölgeli "kutu" bölümlerden oluşuyordu (şablon hissi veren asıl neden), referans sitelerde ise açık arkaplan + çok büyük düz tipografi + neredeyse hiç kutulama yok + çok daha fazla boşluk + gerçek bir nav bar vardı.

Kullanıcı onayıyla 4 yapısal değişiklik uygulandı (`templates/index.html`):
1. **Üst nav bar eklendi** — logo (mevcut `static/logo.png`) + "CV Doktoru" wordmark + "Nasıl Çalışır/Örnek Analiz/SSS" çapa linkleri + "Ücretsiz Analiz" CTA'sı, sticky+blur.
2. **Hero koyu lacivert temadan açık temaya geçti** — `linear-gradient(180deg, #F0F9FF, #F8FAFC)`, tipografi koyulaştırıldı (#0F172A), gradient blob/nokta deseni dekorasyonları kaldırıldı, hero-visual-card'daki -2deg rotate ve koyu kart arkaplanı kaldırıldı (artık düz, beyaz, "gerçek ürün" hissi veren bir kart).
3. **Kutulama azaltıldı** — rozet şeridi, "3 Adımda Sonuç" ve SSS bölümleri artık `.section-flat`/`.faq-wrap` ile kutu/border/gölge olmadan sayfa arkaplanında duruyor. Kutu (border+gölge) sadece gerçekten "özel" 3 unsurda kaldı: form (fonksiyonel giriş alanı), "Derin Analiz Paketi" teklif kartı, "Rapor Neye Benziyor" demo kartı — referans sitelerdeki kalıpla aynı mantık.
4. **Boşluk arttırıldı** — yeni `.section-flat`/`.section-spaced` sınıflarıyla bölümler arası dikey boşluk ~2 katına çıkarıldı (1.5rem → 3-4.5rem).

Ayrıca form altındaki eski `.trust-bar` (düz metin pill şeridi) kaldırıldı çünkü artık hero altındaki yeni rozet şeridiyle tamamen tekrar ediyordu — ölü/tekrarlı CSS de temizlendi.

**Önemli metodoloji düzeltmesi (mobil test):** Önceki oturumlarda "mobilde (390px) hero başlık/rozet metinleri sağdan taşıp kesiliyor" diye kaydedilen bug, bu oturumda **CDP `Emulation.setDeviceMetricsOverride` ile gerçek mobil emülasyonla yeniden test edildi ve gerçek bir hata olmadığı, sadece `chrome --window-size=390,...` ekran görüntüsü yönteminin bir artefaktı olduğu doğrulandı** — düzgün mobil emülasyonla hiçbir taşma yok, tüm metinler doğru sarılıyor. **Kural:** Bundan sonra mobil doğrulama için mutlaka CDP `Page.enable` + `Emulation.setDeviceMetricsOverride({mobile:true})` + `Page.captureScreenshot` akışı kullanılacak (script: `scratchpad/cdp_mobile_shot.py` tarzı, kalıcı değil ama yöntem tekrarlanabilir). Düz `--window-size` ile alınan mobil ekran görüntülerine güvenilmeyecek. Bu nedenle önceki checkpoint'lerdeki "mobil taşma bug'ı, düzeltilmedi" notu **yanlış pozitifti, artık geçersiz.**

Yerelde (port 8533) hem masaüstü (1440px, tam sayfa) hem doğru CDP mobil emülasyonuyla (390px, tam sayfa) doğrulandı, ekran görüntüleri kullanıcıya gösterildi. Kullanıcı onayladı, commit `fe25d49` push edildi, sunucuya deploy edildi, canlıda `curl` ile doğrulandı (HTTP 200, yeni `navbar-brand`/`section-flat` sınıfları mevcut).

## Bu Oturumda Yapılanlar (devam) — SSS Bölümü Genişletildi (Arama + 12 Soru)

Kullanıcı React/TypeScript/Tailwind ile hazır bir FAQ bileşeni istedi, ama proje bu yığını hiç kullanmıyor (FastAPI + Jinja2 + vanilla CSS/JS, `package.json`/`tailwind.config`/`tsconfig` yok). Bu uyuşmazlık kullanıcıya açıkça iletildi; kullanıcı "mevcut siteye vanilla HTML/CSS/JS olarak entegre et" seçeneğini onayladı — React kodu üretilmedi.

`templates/index.html`'deki SSS bölümü (`#faq`) baştan yazıldı:
- Eski `<details>/<summary>` yapısı, buton + `grid-template-rows: 0fr → 1fr` CSS geçişiyle animasyonlu özel bir accordion'a dönüştürüldü (native `<details>` smooth height transition desteklemiyor).
- 5 sorudan **12 soruya** çıkarıldı: KVKK/veri saklama, ATS nedir/nasıl çalışır, analiz kapsamı (sadece gramer değil), ücretlendirme/gizli maliyet yok, süre, tekrar analiz hakkı, yapay zeka vs. İK uzmanı, yabancı dil desteği, Canva/görsel şablon riski, mülakat garantisi **olmadığı** (dürüst, CLAUDE.md ilkesiyle uyumlu — false promise yapılmadı), dosya formatları, veri silme talebi (zaten hiç saklanmadığı için gereksiz olduğu açıklandı).
- Üstte arama çubuğu eklendi (`#faq-search-input`) — JS ile soru başlıklarını (`data-q` attribute, Türkçe locale-aware `toLocaleLowerCase('tr-TR')`) anlık filtreliyor, sonuç yoksa "Aramanızla eşleşen bir soru bulunamadı" mesajı çıkıyor.
- Altta destek CTA'sı eklendi — kullanıcı henüz gerçek bir destek e-postası/kanalı vermediği için **link olmadan, nötr bir not** olarak bırakıldı ("Yakında buradan destek ekibimize de ulaşabileceksiniz."); ileride gerçek bir destek kanalı belirlenirse mailto: linkine çevrilmeli.

**Test yöntemi:** CDP (`Emulation.setDeviceMetricsOverride`) ile gerçek tarayıcıda otomatik JS tıklama (`Runtime.evaluate` + `.click()`) ve arama input event'i tetiklenerek doğrulandı — accordion açılıyor, arama filtresi doğru soruyu buluyor, "bulunamadı" durumu doğru tetikleniyor. Yerelde (port 8534) ekran görüntüleriyle onaylandı. **Henüz commit/deploy edilmedi.**

## Açık Kalan Sorular / Sıradaki Adımlar
- [x] **Öncelik:** Rozet şeridi seçildi ve eklendi (yukarıya bakın). Kalan 2 unsur (hero foto, sosyal kanıt şeridi) henüz uygulanmadı.
- [ ] "Bunu ben yaptım" founder fotoğraf bölümü — kullanıcı fotoğraf sağladığında ekle.
- [ ] Sosyal kanıt şeridi — CLAUDE.md dürüstlük ilkesi gereği gerçek sayı/isimli yorum olmadan uygulanamaz, trafik/lead verisi büyüyünce tekrar değerlendir.
- [x] Kapsamlı redesign (nav bar, açık hero, az kutulama, çok boşluk) — commit `fe25d49`, deploy edildi, canlıda doğrulandı.
- [x] Mobil taşma bug'ı — **yanlış pozitifmiş**, CDP ile doğru mobil emülasyonla test edilince hata yok. Bundan sonra mobil test CDP ile yapılacak (yukarıya bakın).
- [ ] Mobilde (390px) hero başlık/rozet metinlerinin taşıp kesilmesi sorunu — kullanıcı "sonra bakarız" dedi, düzeltilmedi.
- [ ] Fake-door testi bir sonraki 3-4 günlük döngüde tekrar ölçülecek mi yoksa tasarım değişikliğinden sonra mı — henüz kararlaştırılmadı.
- [ ] 5 adımlık tasarım planının 4. maddesi — mikro-etkileşim/scroll animasyonları + mobilde sticky CTA bar — henüz başlanmadı.
- [ ] Kendi IP'yi analytics sayımından hariç tutma filtresi (kullanıcı henüz "yap" demedi).
- [ ] Search Console → URL Inspection → "Request Indexing" hâlâ yapılmadı.
- [ ] FastAPI sürümünü mobil dahil gerçek cihazlarla kapsamlı test et (dosya yükleme akışı ayrıca doğrulanmadı).

## Bilinen Riskler / Dosya Notları
- Proje kökünde `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` ve `Logo.png` hâlâ commit edilmemiş kaynak dosyalar olarak duruyor — dokunma, kullanıcının kendi dosyaları.
- İki venv karışıklığı (`venv/` vs `source/`) — `venv/` çalışan, `source/`'da fastapi yok, kullanma.
- Yerel test yöntemi: `"./venv/Scripts/python.exe" -m uvicorn src.server:app --host 127.0.0.1 --port 85XX` + headless Chrome. Mobil genişlik testi için CDP `Emulation.setDeviceMetricsOverride` kullan (`--window-size` tek başına yeterli değil).
- Prompt değişikliklerini gerçek API çağrısıyla test etmek için: `.env`'de `ANTHROPIC_API_KEY` mevcut, `"./venv/Scripts/python.exe"` ile `src.analyzer.CVDoctor().analyze(cv_text, job_ad)` doğrudan çağrılabilir (Windows konsolunda emoji içeren sonucu `print()` etme — `cp1254` codec `UnicodeEncodeError` verir, dosyaya UTF-8 ile yaz).
