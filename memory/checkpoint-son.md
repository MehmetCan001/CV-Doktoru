# CHECKPOINT — 2026-07-24 — v1.12

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

**Test yöntemi:** CDP (`Emulation.setDeviceMetricsOverride`) ile gerçek tarayıcıda otomatik JS tıklama (`Runtime.evaluate` + `.click()`) ve arama input event'i tetiklenerek doğrulandı — accordion açılıyor, arama filtresi doğru soruyu buluyor, "bulunamadı" durumu doğru tetikleniyor. Yerelde (port 8534) ekran görüntüleriyle onaylandı.

**Ek bulgu — CLAUDE.md çelişkisi düzeltildi:** Commit öncesi `git status` kontrolünde, `CLAUDE.md`'nin de değiştiği görüldü — kullanıcı (muhtemelen IDE'de dosya açıkken, React/Tailwind FAQ isteğiyle aynı kaynaktan) React/TypeScript/Tailwind/shadcn/framer-motion'ı zorunlu kılan 45 satırlık bir bölüm yapıştırmış; bu, projenin gerçek yığınıyla (FastAPI+Jinja2+vanilla) doğrudan çelişiyordu. Kullanıcıya soruldu, "projemizin özelliklerine uygun şekilde düzenle" dedi. Bölüm silinmedi, içeriği gerçek yığına ve bu oturumda kurulan tasarım yönüne (açık tema, az kutulama, çok boşluk, CDP mobil test kuralı) göre yeniden yazıldı.

Commit `08626d3`, push edildi, sunucuya deploy edildi, canlıda `curl` ile doğrulandı (HTTP 200, `faq-search-input` mevcut, 12 `faq-item`).

## Bu Oturumda Yapılanlar (devam) — Fake-Door Sonucu (2. Ölçüm) ve Strateji Kararı

İkinci fake-door ölçümü geldi: `days:14, unique_visitors:51, premium_click_visitors:2, leads_captured:1, click_rate_pct:3.9, lead_conversion_pct:2.0, verdict:OPTIMIZE`.

Kullanıcı "Google Ads verelim mi, fiyatı mı değiştirelim?" diye sordu. Değerlendirme: n=51 hâlâ çok küçük, üstelik bu pencere büyük ölçüde redesign'dan (nav bar, açık hero, genişletilmiş SSS) ÖNCEKİ tasarımı kapsıyor — veri yeni tasarımın etkisini yansıtmıyor. **Tavsiye edilip kullanıcı tarafından onaylandı:** Google Ads'e para harcamadan önce yeni tasarımla temiz bir 7-10 günlük ölçüm penceresi daha bekle, organik trafiğe devam et. Fiyat değişikliği için de yeterli sinyal yok (1 lead, 0 gerçek ödeme) — fiyatın mı görünürlüğün mü darboğaz olduğu belirsiz, şimdi değiştirmek tahmin olur.

**Kullanıcı tasarım yönünde net bir geri bildirim verdi (önemli, gelecek oturumlar için):** Mevcut redesign (nav bar + açık hero + az kutulama + çok boşluk) istediği yerden **çok uzak**. İstediği: **fotoğraf, animasyon, GIF ile dolu dolu, estetik, sıcak, güvenilir, samimi VE profesyonel** bir görünüm. Bu, önceki oturumlarda uyguladığımız "minimalist, düz, az dekorasyon, Stripe/Linear tarzı flat" yönünün ötesinde/farklısında bir talep — kullanıcı daha **zengin, duygusal, görsel açıdan dolu** bir sonuç istiyor, sadece yapısal sadeleştirme (nav bar, boşluk artırma) yeterli değil. **Yarın devam edilecek, henüz hiçbir yeni tasarım kararı alınmadı/uygulanmadı.** Yarın ilk iş: bu "sıcak/samimi/görsel dolu" hedefini somut olarak ne anlama geldiğini (hangi referanslar, hangi görsel unsurlar, founder fotoğrafı/gerçek insan görüntüsü var mı) netleştirmek.

## Bu Oturumda Yapılanlar (2026-07-24) — Sıcak/Samimi Tam Yeniden Tasarım (v1.12)

Önceki oturumun açık sorusu ("sıcak, samimi, fotoğraf/animasyon dolu, profesyonel" hedefi somutlaştırılmalı) bu oturumda çözüldü ve uygulandı.

**Karar süreci:** Kullanıcıya 3 somut yön önerildi (A: solo-founder odaklı, B: sıcak renk+illüstrasyon odaklı, C: hibrit/mevcut yapıyı koru). Kullanıcı hibrit öneriyi reddetti, "mevcut yapıyı korumanı istemiyorum, sıfırdan baştan aşağı yeniden tasarla" dedi — hem görsel dil hem yerleşim/bölüm sırası baştan kurgulandı.

**Founder fotoğrafı:** Kullanıcı `static/20250928_124229.jpg` (5.3 MB, EXIF orientation 6 ile yan yatık kaydedilmiş telefon fotoğrafı) yükledi. `PIL.ImageOps.exif_transpose` ile doğru yöne çevrildi, yüz+omuz odaklı kare kırpıldı (900x900 önizleme onaylandı), `static/founder-photo.jpg` olarak 800x800/90KB'a optimize edildi. **Ders:** Kullanıcıdan telefon fotoğrafı istenirken EXIF orientation kontrolü rutin bir adım olmalı — ham pikseller genelde yan/ters görünür, `exif_transpose` olmadan kırpma yanlış alanı keser.

**Tasarım:** `templates/index.html` tamamen yeniden yazıldı (Write ile, önceki 1059 satırlık dosyanın üzerine):
- Palet: lacivert/mavi yerine krem (`#FBF5EB`) + terracotta (`#DD5C22`) + sıcak kahve (`#271F16`) — CSS custom property (`:root` değişkenleri) ile.
- Tipografi: Başlıklar için `Fraunces` (serif, sıcak/karakterli), gövde metni için `Inter` — iki fontlu kontrast.
- Hero: Founder fotoğrafı (46px yuvarlak avatar) + "Merhaba, ben Mehmet..." samimi cümle + otomatik üretilen ürün akış GIF'i (aşağıya bakın).
- Yeni "founder-note" bölümü: büyük fotoğraf (96px) + alıntı tarzı kişisel not, hero altına eklendi.
- Tüm koyu-lacivert gradient'ler (demo-header, premium-card, cv-loading-card, report-header-card) sıcak kahverengi gradient'e (`--dark`/`--dark-2`) çevrildi.
- Scroll-reveal mikro-animasyonları: `IntersectionObserver` + `.reveal`/`.reveal-stagger` CSS sınıfları, `prefers-reduced-motion` desteğiyle.
- **Kritik:** Tüm JS-bağımlı ID/class'lar (`analyze-form`, `cv-file`, `faq-item`/`data-q`, `tab-btn`/`tab-pane`, `premium-*`, `report-*`, `cv-loading-*`, `alert-*`, `download-btn`) birebir korundu — sadece CSS/HTML iskeleti değişti, JS mantığına dokunulmadı (sadece reveal-observer script'i eklendi).

**Ürün akış GIF'i (`static/urun-akisi.gif`, ~500KB):** Yerel `uvicorn` sunucusu ayağa kaldırılıp CDP (Chrome DevTools Protocol, websocket-client ile doğrudan) üzerinden otomatik olarak üretildi — gerçek sayfa, gerçek DOM, gerçek CSS/JS ile form dolduruluyor (örnek/kurgusal CV+ilan metni, mevcut "ÖRNEK · DEMO" kartındakiyle tutarlı dürüstlük ilkesinde), Analizi Başlat'a tıklanıyor, loading kartı ve rapor gösteriliyor. **Backend gerçek Claude API'ye bağlanmadı** (2-3 dakika sürer ve API kredisi harcar) — bunun yerine `Page.addScriptToEvaluateOnNewDocument` ile sayfaya enjekte edilen bir `window.fetch` shim'i, `/api/analyze/start` ve `/api/analyze/status/*` çağrılarını yakalayıp gerçekçi bir zamanlama ile (poll aralığına uygun ~6sn sonra) sabit örnek bir rapor metni döndürdü. Gerçek ürün kodu (renderMarkdown, renderReport, loading animasyonu) hiç değiştirilmeden, sadece ağ katmanı simüle edilerek çalıştırıldı — GIF'in altyazısı bunu "gerçek arayüzden akış — örnek CV ve ilan metniyle" diye dürüstçe belirtiyor, "canlı gerçek zamanlı analiz" iddiası yok.

**Test yöntemi:** CDP ile hem 1440px masaüstü hem 390px mobil (doğru `Emulation.setDeviceMetricsOverride`) tam sayfa ekran görüntüsü alındı; ayrıca otomatik JS tıklama/olay tetikleme ile SSS accordion açma, SSS arama (eşleşen + eşleşmeyen durum), sekme geçişi (PDF/Metin), premium lead formu açılışı ve scroll-reveal animasyonlarının hepsinin `in-view` durumuna geçtiği doğrulandı.

**Bulunan ve düzeltilen bug (bu oturum içinde, deploy öncesi):** İlk yazımda `.reveal-stagger` konteyneri (3 Adımda Sonuç ikonları) IntersectionObserver tarafından hiç gözlemlenmiyordu çünkü observer sadece `.reveal` sınıfını sorguluyordu — adım ikonları kalıcı olarak görünmez kalıyordu. `.reveal, .reveal-stagger` şeklinde düzeltildi. **Ders:** Farklı CSS sınıfı kullanan ama aynı gözlemciye ihtiyaç duyan elementler eklenirken observer'ın sorgu seçicisi güncellenmemesi sessiz bir görünmezlik hatasına yol açar — yeni bir `reveal-*` varyantı eklerken observer selector'ünü de güncellemek gerekir.

**Temizlik notu:** Ekran görüntüsü/GIF üretim scriptleri proje kökünde yanlışlıkla `scratchpad_local/` klasörü oluşturdu (doğru scratchpad yolunun dışında) — commit öncesi fark edilip silindi. Kullanıcının yüklediği ham `static/20250928_124229.jpg` (5.3MB, işlenmemiş orijinal) bilinçli olarak commit'e dahil edilmedi (sadece işlenmiş `founder-photo.jpg` eklendi) — repoda gereksiz büyük dosya birikmesin diye.

Commit `b0b263c`, push edildi, sunucuya deploy edildi (`git pull` + `systemctl restart cv-doktoru`), canlıda doğrulandı: ana sayfa HTTP 200, `/static/founder-photo.jpg` HTTP 200, `/static/urun-akisi.gif` HTTP 200, `founder-note`/`reveal-stagger` içerikleri sayfada mevcut.

**Henüz yapılmayan/açık:** Bu redesign sonrası fake-door ölçüm penceresi sıfırdan başlamalı (önceki pencere hem eski tasarımı hem de ara redesign'ı kapsıyordu, artık geçersiz bir karşılaştırma temeli). Kullanıcıya henüz yeni bir ölçüm takvimi önerilmedi.

## Açık Kalan Sorular / Sıradaki Adımlar
- [x] "Sıcak, samimi, fotoğraf/animasyon/GIF dolu, profesyonel" tasarım hedefi somutlaştırıldı ve uygulandı (yukarıya bakın, commit `b0b263c`).
- [ ] **Yeni öncelik:** Bu köklü redesign sonrası fake-door ölçüm penceresini sıfırla — kullanıcıyla ne zaman/nasıl değerlendirileceğini netleştir (önceki iki ölçüm artık eski tasarımlara ait, geçersiz karşılaştırma).

## Fake-Door 3. Ölçüm Geldi (2026-07-24 sonu) — Değerlendirilmedi, Yarın İlk İş

Redesign deploy edildikten hemen sonra kullanıcı şu veriyi paylaştı: `days:14, unique_visitors:39, premium_click_visitors:2, leads_captured:1, total_leads_all_time:1, click_rate_pct:5.1, lead_conversion_pct:2.6, verdict:GREEN_LIGHT, verdict_detail:"Tıklama oranı %5'in üzerinde — pazar talebi doğrulandı. MVP mimarisine geçilebilir."`

**Kullanıcı ayrıca "sayı düşüyor" dedi** (unique_visitors: 55 → 51 → 39, düşüş trendi) — bu **henüz değerlendirilmedi**, oturum "yarın devam edelim" ile bitti.

**Yarın ilk iş, dikkat edilmesi gerekenler:**
1. Bu 14 günlük pencere büyük ölçüde bugünkü redesign'dan ÖNCEKİ tasarımı kapsıyor (redesign en son deploy edildi) — GREEN_LIGHT verdict'i yeni tasarımın etkisini yansıtmıyor, otomatik karar matrisi bunu bilemez, körü körüne "MVP'ye geç" denmemeli.
2. **Ziyaretçi sayısındaki düşüş trendi** (55→51→39) ayrı ve muhtemelen daha acil bir sinyal — click_rate/lead_conversion yükseliyor gibi görünse de bu küçük n (39 ziyaretçi, 2 tıklama, 1 lead) üzerinde yüzdesel dalgalanma da olabilir. Düşüşün kök nedenini araştırmadan (organik trafik mi azaldı, SEO/Search Console durumu ne, mevsimsel mi) yorum yapmamalı.
3. Search Console → "Request Indexing" hâlâ yapılmamıştı (bkz. eski açık madde) — trafik düşüşüyle ilişkili olabilir, kontrol edilmeli.
- [ ] Google Ads kararı ertelendi — yeni tasarımla 7-10 günlük temiz bir ölçüm penceresi bekleniyor, sonra tekrar değerlendirilecek.
- [ ] Fiyat değişikliği ertelendi — yeterli veri yok.
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

## Bu Oturumda Yapılanlar (2026-07-29) — Trafik Düşüşü Araştırması + Bot Filtresi

**Trafik düşüşü (55→51→39) araştırıldı — gerçek bir trend DEĞİL:**
- Sunucudaki `analytics_events.jsonl` günlük kırılımı: taban trafik günde 1-6 tekil ziyaretçi; 10 Temmuz'da tek günlük 15'lik spike vardı, o gün 14 günlük pencereden çıktıkça toplam "düşüyor" göründü. Taban hiç değişmedi — asıl sorun düşüş değil, trafiğin zaten yok denecek kadar az olması.
- **Sayaçlar bot içeriyordu:** nginx loglarında `POST /api/track/visit` isteklerinde HeadlessChrome (muhtemelen bizim canlı doğrulama screenshot'larımız), Googlebot render'ı, Dataprovider.com ve sahte tam-sürümlü Chrome UA'ları (`Chrome/145.0.7632.6` aynı gün hem Windows hem Android'den — otomasyon) tespit edildi. Önceki fake-door verdict'leri (GREEN_LIGHT dahil) bu kirlilik nedeniyle güvenilmez.
- **Önemli teknik ders (yanlış varsayım düzeltildi):** `Chrome/150.0.0.0` gibi sıfırlanmış sürüm bot işareti DEĞİL — Chrome 101+ gerçek tarayıcılar UA reduction gereği daima `MAJOR.0.0.0` gönderir. Asıl anomali TAM sürüm bildiren Chrome 101+ UA'sıdır (gerçek tarayıcı bunu yapmaz → spoof).
- 19 Temmuz'daki 624 istekli "Googlebot" taraması sahte Googlebot'tu — `.env`/`wp-config.php` arayan zafiyet tarayıcısı, hepsi 404 aldı, sızıntı yok. Gerçek Googlebot günde 4-12 istekle normal tarıyor.
- Reddit/HN/Facebook referrer'ları referrer-spam botları (IP'ye doğrudan `.asp` yollarıyla geliyorlar). Gerçek organik kaynak sadece Google, günde ~1-9 istek.

**Bot filtresi eklendi (commit `c290d9e`, deploy edildi, canlıda doğrulandı):**
- `src/analytics.py`: `is_bot_user_agent()` — bot/headless/crawl/python/curl vb. anahtar kelimeler + boş UA + Chrome≥101 tam-sürüm anomalisi. 13 gerçek UA örneğiyle test edildi, hepsi geçti.
- `ANALYTICS_EXCLUDE_IPS` env desteği (virgülle ayrılmış) — kullanıcının ev IP'si (`176.54.59.46`, SSH_CLIENT'tan tespit edildi) sunucu `.env`'ine eklendi. **Dikkat: ev IP'si dinamik olabilir (Türk ISS'leri), değişirse sunucuda `.env` güncellenmeli.**
- `src/server.py` track endpoint'leri UA'yı `log_event`'e geçiriyor; `log_event(event, ip, user_agent=None)` geriye uyumlu.
- Canlı doğrulama: curl UA'lı ve gerçek-Chrome-UA'lı-ama-hariç-IP'li iki test isteği atıldı, olay dosyası 205→205 satır (ikisi de sayılmadı). Endpoint botlara bilgi sızdırmamak için yine `{"ok":true}` döner.
- **Not:** Geçmiş veri retroaktif temizlenemez (olay dosyasında UA saklanmıyor) — redesign sonrası ölçüm penceresi zaten sıfırdan başlayacaktı, temiz veri bundan sonra birikecek.

**Açık kalan (bu araştırmadan çıkan):**
- [x] Search Console → Request Indexing — 2026-07-31'de kullanıcı tarafından yapıldı (bkz. aşağıdaki 2026-07-31 bölümü).
- [ ] Asıl darboğaz trafik edinimi: fake-door'un anlamlı sonuç vermesi için önce gerçek trafik lazım. İçerik/SEO veya küçük bütçeli Ads tartışması öne çekilmeli (Ads kararı önceden ertelenmişti).

## Bu Oturumda Yapılanlar (2026-07-31) — SEO/İndeksleme Teşhisi + Request Indexing

Trafik düşüklüğünün kök nedeni araştırıldı. `WebSearch` ile `site:cvdoktoru.com` sorgusu **sıfır sonuç** döndürdü, genel "cvdoktoru CV analiz yapay zeka" araması da siteyi hiç göstermedi — site muhtemelen Google tarafından hiç indekslenmemişti.

**Teknik taraf doğrulandı, engel yok:** Canlı `curl` ile kontrol edildi — `<meta name="robots" content="index, follow">` doğru, `X-Robots-Tag` header'ı yok, `canonical` doğru (`https://cvdoktoru.com/`), `title`/`description`/OG etiketleri sağlıklı, `robots.txt` ve `sitemap.xml` doğru serviste (dinamik, `src/server.py`).

**Sonuç:** Sorun kod/config değil — muhtemelen Search Console'da "Request Indexing" hiç tetiklenmemiş olması + domain'in yeni olup henüz organik keşfedilmemiş olması. Kullanıcıya bu adım manuel olarak (kendi Google hesabıyla) yaptırıldı, kullanıcı "dizine ekleme istedim" diye onayladı.

**Sıradaki adım (birkaç gün sonra kontrol edilecek):** Search Console → URL Inspection → "Sayfa Google'da mı?" durumuna bak + Performans raporunda gösterim (impression) sayısı 0'dan çıktı mı bak. İndeksleme genelde saatler-birkaç gün sürer, hemen sonuç beklenmemeli.

## Bu Oturumda Yapılanlar (2026-08-01) — Mobil Test Bug'ları + UI Skill Kurulumu

Kullanıcı LinkedIn paylaşımı öncesi telefondan gerçek mobil test yaptı, 2 gerçek bug buldu — ikisi de aynı oturumda kök nedeniyle bulunup düzeltildi ve canlıya deploy edildi.

### Bug 1: PDF raporu hiç inmiyordu
**Kök neden:** `src/pdf_export.py::_find_unicode_fonts()` sadece sabit OS yollarında (`/usr/share/fonts/truetype/dejavu/...`, `/usr/share/fonts/truetype/liberation/...`) font arıyor; sunucuda (Ubuntu 26.04) bu font paketleri hiç kurulu değildi, hatta `fontconfig` bile yoktu. Fonksiyon `(None, None)` döndürüp `generate_pdf_report` her seferinde `RuntimeError` fırlatıyordu → `/api/pdf` sessizce 500 veriyordu.
**Düzeltme:** Sunucuya `apt-get install -y fonts-dejavu-core` kuruldu (kod değişikliği yok, sistem paketi). SSH ile doğrulandı: `ls /usr/share/fonts/truetype/dejavu/` artık dosyaları listeliyor, `systemctl restart cv-doktoru` sonrası canlı `/api/pdf` testi HTTP 200 + geçerli PDF döndü.

### Bug 2: PDF'te metin header arka planıyla üst üste biniyordu
**Kök neden:** `pdf_export.py` header dikdörtgenini 32pt yükseklikte çiziyordu (`pdf.rect(0,0,210,32,"F")`), ama başlık hücresinden sonra `pdf.ln(6)` ile içerik y=28'den başlıyordu — 28 < 32 olduğu için ilk satırlar koyu lacivert zemin üzerine koyu gri renkte (40,40,40) yazılıp görünmez/karışık oluyordu.
**Düzeltme:** `pdf.ln(6)` yerine `pdf.set_y(40)` — header'ın 8pt net altından başlıyor artık. Commit `5c1d8a0`, deploy edildi, canlı test edildi (Türkçe karakterli örnek raporla).

### Bug 3: TXT indirmede Türkçe karakterler bozuluyordu
**Kök neden:** `templates/index.html`'deki TXT indirme Blob'u `text/plain;charset=utf-8` tipiyle oluşturuluyordu ama BOM (byte order mark) yoktu — bazı mobil görüntüleyiciler BOM'suz UTF-8'i yanlış encoding ile açıyor.
**Düzeltme:** Blob içeriğinin başına UTF-8 BOM (`﻿`, bayt olarak `EF BB BF`) eklendi. Commit `fe009e4`, deploy edildi. **Kullanıcı ilk testte hâlâ bozuk gördü ama muhtemelen tarayıcı önbelleği eski sayfayı gösteriyordu** (curl ile canlı HTML'de BOM'un mevcut olduğu doğrulandı) — kullanıcıdan hard-refresh sonrası tekrar test etmesi istendi, sonucu bu checkpoint'e kadar teyit edilmedi, **yarın ilk iş bunu sormak.**

### Bug 4 (ui-ux-pro-max skill ile bulundu): `.demo-badge` WCAG kontrast yetersizliği
"ÖRNEK · DEMO" rozeti (`--accent` rengi, saydam `--accent` tint zemin üzerinde) hesaplanan kontrastı 2.86:1 idi (WCAG AA küçük metin eşiği 4.5:1). Zaten tanımlı `--accent-dark`/`--accent-softer` token'larına geçilerek (saydam yerine düz renk) 4.5:1 üzerine çıkarıldı, görsel dil bozulmadı. Commit `a1fb825`, deploy edildi.

### `ui-ux-pro-max` design skill kuruldu (proje-özel, `.claude/skills/`)
Kullanıcı https://github.com/nextlevelbuilder/ui-ux-pro-max-skill skill'ini `npm install -g ui-ux-pro-max-cli` + `uipro init --ai claude` ile kurdu. Paket 6 alt skill getirdi (`ui-ux-pro-max`, `banner-design`, `brand`, `design`, `design-system`, `slides`, `ui-styling`). **`ui-styling` kaldırıldı** çünkü Tailwind/shadcn'e özel — CLAUDE.md'nin başındaki uyarıyla birebir çelişen bir risk taşıyordu (proje vanilla CSS kullanıyor). `.claude/` zaten `.gitignore`'da, bu skill dosyaları repoya girmiyor.

**Skill'in gerçek davranışı test edildi, önemli bulgu:** `--design-system` (bütünsel tam-sayfa öneri) modu **güvenilmez** — iki farklı, isabetli sorguda bile projenin kimliğiyle alakasız sonuçlar verdi (bir seferinde koyu lacivert "Enterprise Gateway" B2B stili — tam olarak daha önce reddettiğimiz yön; diğerinde siyah+pembe "Anti-Polish/Raw" el-çizimi indie sanat sitesi stili). Anahtar kelime eşleştirmesi yüzeysel, proje geçmişini/kararlarını bilmiyor. **Buna karşılık `--domain <alan>` ile dar kapsamlı sorgular (color, typography, ux) gerçekten değerli** — Bug 4'ü böyle bulduk. **Kural: Bu skill'i "tasarımcı" gibi kullanma, nokta atışı danışma/doğrulama kaynağı olarak kullan** (özellikle WCAG kontrast kontrolü için); büyük tasarım kararları yine kullanıcıyla birlikte, projenin gerçek bağlamına göre alınmalı.

## Açık Kalan / Yarın İlk İş
- [ ] **TXT indirme BOM düzeltmesinin gerçekten çalıştığını doğrula** — kullanıcı hard-refresh sonrası tekrar test etmedi/sonucu paylaşmadı.
- [ ] LinkedIn paylaşımı hâlâ yapılmadı — mobil bug'lar düzeltildi, paylaşım metni ve profil güncellemesi (headline/about/deneyim) bu oturumda hazırlandı ama henüz LinkedIn'e girilmedi/paylaşılmadı, kullanıcı elle giriyor.
- [ ] FastAPI dosya yükleme akışı gerçek mobil cihazda test edildi ve **çalıştığı doğrulandı** (bu oturumda) — eski açık madde kapatılabilir.

## Bilinen Riskler / Dosya Notları
- Proje kökünde `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` ve `Logo.png` hâlâ commit edilmemiş kaynak dosyalar olarak duruyor — dokunma, kullanıcının kendi dosyaları.
- İki venv karışıklığı (`venv/` vs `source/`) — `venv/` çalışan, `source/`'da fastapi yok, kullanma.
- Yerel test yöntemi: `"./venv/Scripts/python.exe" -m uvicorn src.server:app --host 127.0.0.1 --port 85XX` + headless Chrome. Mobil genişlik testi için CDP `Emulation.setDeviceMetricsOverride` kullan (`--window-size` tek başına yeterli değil).
- Prompt değişikliklerini gerçek API çağrısıyla test etmek için: `.env`'de `ANTHROPIC_API_KEY` mevcut, `"./venv/Scripts/python.exe"` ile `src.analyzer.CVDoctor().analyze(cv_text, job_ad)` doğrudan çağrılabilir (Windows konsolunda emoji içeren sonucu `print()` etme — `cp1254` codec `UnicodeEncodeError` verir, dosyaya UTF-8 ile yaz).
