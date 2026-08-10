# Rakip Farklılaşma Stratejisi — Tasarım

**Tarih:** 2026-08-08
**Durum:** Faz 0 onaylandı, uygulamaya geçiliyor. Faz 1-4 üst düzeyde onaylandı, detaylar ileride ayrı oturumlarda netleştirilecek.

## Bağlam

Bu oturumda üç rakip derinlemesine incelendi (canlı siteye girilerek, DOM/network analiziyle doğrulandı):

- **cvanaliz.com.tr** — Google'da "cv analiz" aramasında 1. sırada, ama gerçek ürün bir Hugging Face Space'te (ücretsiz/hobi altyapısı) çalışıyor, Gemini kullanıyor, hiçbir monetizasyon sinyali yok. Muhtemelen para kazanmıyor; SEO gücü sadece domain adının aratılan kelimeyle birebir eşleşmesinden geliyor.
- **cvanaliz.com** — Next.js tabanlı, kapsamlı bir SaaS (analiz + builder + mülakat + ön yazı + B2B ATS + blog + maaş verisi), gerçek fiyatlandırma (39-159₺) var. Ama güven katmanı kırık: KVKK metninde doldurulmamış AI-şablon parantezi, hiç Mersis/vergi no yok, PRO+ paket açıklamasında "qwe" placeholder metni canlıda duruyor. Muhtemelen para kazanmıyor ya da çok erken aşamada.
- **CVCIM** — İncelenen rakipler arasında **gerçekten para kazandığı somut kanıtlarla doğrulanan tek örnek**: kayıtlı şirket (Moose Danışmanlık Yazılım Elektronik Ltd. Şti., Ticaret Sicil No: 415450), 2010'dan beri faaliyette (16 yıl), canlı iyzico entegrasyonu, tam yasal uyum belgeleri (Mesafeli Satış Sözleşmesi vb.), ₺249-499 aralığında insan-danışmanlık hizmeti (3 gün teslimat, atanmış danışman + telefon görüşmesi).

**Kilit çıkarım:** Türk kullanıcı CV danışmanlığına gerçekten para ödüyor (CVCIM bunu kanıtlıyor), ama hiçbir rakip "hız + otomasyon + doğru fiyat + gerçek güven" kombinasyonunu birlikte sunmuyor. cvanaliz'ler üründe iyi ama güvende kötü; CVCIM güvende iyi ama yavaş/pahalı/insan-kapasitesiyle sınırlı.

## Alınan Kararlar

1. **Gelir modeli: Freemium.** Temel analiz ücretsiz/sürtünmesiz kalır (mevcut durum). Üstüne, mevcut fake-door testi yapılan "Derin Analiz Paketi" konseptini gerçek ödemeli ürüne dönüştürüyoruz — CVCIM'in ₺249'una karşı çok daha ucuz ve anlık.
2. **İnsan dokunuşu eklenmiyor.** CVCIM'in "bir insan CV'ne bakıyor" avantağına karşı insan-destekli üst paket kurmuyoruz (tek kişilik ekip için operasyonel olarak ölçeklenmez). Bunun yerine hız (30 saniye vs 3 gün), fiyat, ilana-özel derinlik ve Türk iş kültürü nüansıyla farklılaşıyoruz.
3. **Kapasite: Solo + küçük bütçe.** Plan buna göre sıralanıyor — önce en ucuz/hızlı adımlar, pahalı/riskli adımlar (ücretli reklam, SEO içerik yatırımı) en sona bırakılıyor, çünkü ancak o noktada elimizde onları anlamlı kılacak trafik/veri olacak.

## Genel Strateji: 5 Fazlı Merdiven

**Seçilen sıralama (Yaklaşım 1):** Güven → Dağıtım → Para Kazanma → SEO → Ölçek. Gerekçe: sıralama en ucuz/az riskli adımdan en pahalı/riskli adıma doğru ilerliyor; her faz bir sonrakini anlamlı kılacak veriyi/temeli üretiyor (örn. ödeme sistemini trafik yokken kurmak ya da güvenilir görünmeden dağıtıma çıkmak boşa efor olurdu).

| Faz | Süre | Odak | Çıkış kriteri |
|---|---|---|---|
| 0 | Bu hafta | Güven katmanı | Site canlıda, footer + gizlilik/iletişim + "nasıl analiz ediyoruz" sayfası var |
| 1 | 2-4 hafta | Dağıtım (LinkedIn, kariyer toplulukları, üniversite kulüpleri) | Haftalık gerçek kullanıcı sayısı ölçülebilir şekilde artıyor |
| 2 | 1-2 ay | Derin Analiz Paketi → gerçek ürün (iyzico) | İlk gerçek ödeme alınıyor |
| 3 | 2-4 ay | SEO/içerik momentumu + küçük reklam bütçesi testi | Organik trafik büyüyor, huninin dönüşüm verisi var |
| 4 | 6-12 ay | Ölçek (B2B — üniversite kariyer merkezi ortaklığı, PR) | Tekrarlayan/öngörülebilir bir gelir kanalı |

Faz 1-4'ün detaylı spec'i bu doküman kapsamında değil — her biri kendi zamanı geldiğinde ayrı bir brainstorming/spec turundan geçecek (kullanıcı tercihi, 2026-08-08).

## Faz 0 — Güven Katmanı (Detaylı Spec)

**Gerekçe:** Sitede şu an hiçbir resmi güven sinyali yok — footer tek satır (`CV Doktoru — Türkiye'nin iş ilanına özel CV analiz aracı`), İletişim/Gizlilik/KVKK sayfası ya da route'u hiç yok (`src/` içinde bu terimler için sıfır eşleşme doğrulandı). Founder fotoğrafı + isim (`templates/index.html` — hero ve founder-note bölümleri) zaten var ve iyi bir temel; eksik olan resmi/hukuki şeffaflık katmanı.

**Kapsam (yapılacaklar):**
1. Footer'a gerçek bilgi eklenir: iletişim e-postası, "Gizlilik" ve "Nasıl Çalışır" linkleri.
2. Basit bir Gizlilik/KVKK sayfası eklenir — doğru ve dolu bir metinle (cvanaliz.com'daki doldurulmamış şablon hatasının tam tersi). Mevcut doğru uygulamayı (CV analiz sonrası saklanmıyor/siliniyor) açıkça anlatır.
3. Kısa bir "Nasıl Analiz Ediyoruz" şeffaflık bloğu eklenir: hangi model (Claude) kullanılıyor, hangi kriterlere bakılıyor, ne garanti edilmiyor.

**Kapsam dışı (bilinçli olarak yapılmayacak — YAGNI):** Resmi şirket kurmak, Mersis/vergi no almak. Bu bir hukuki/mali karar, kod değişikliği değil, ve Faz 0'ın amacı bu değil. Konumlanma "kayıtlı şirket" değil, "gerçek isim + tam şeffaflık" üzerinden kuruluyor.

**Netleşen karar:** CV Doktoru şahıs olarak yürütülüyor, kayıtlı bir şirket yok (2026-08-08). Gizlilik/KVKK metninde "Veri Sorumlusu" gerçek ve tam isimle (Mehmet Can ALIN — 2026-08-10'da netleşti) yazılır, şirket unvanı/vergi no/ticaret sicil no gibi var olmayan bilgiler **eklenmez** — cvanaliz.com'un yaptığı "varmış gibi" görünme hatasına düşülmez, dürüstlük ilkesi (CLAUDE.md Bölüm 6/11) korunur.

## Test / Doğrulama

- Footer linkleri ve yeni sayfalar mobil dahil gerçek cihazda görsel kontrol edilecek (bkz. proje CLAUDE.md — headless Chrome native screenshot güvenilmez, CDP `Emulation.setDeviceMetricsOverride` kullanılmalı).
- Gizlilik/KVKK metninin gerçek uygulamayla (verinin gerçekten saklanmadığı) tutarlı olduğu `src/` koduna bakılarak doğrulanacak — iddia edilen her cümle kodda karşılığı olmalı.
