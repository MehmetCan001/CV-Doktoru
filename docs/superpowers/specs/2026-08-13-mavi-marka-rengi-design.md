# Turuncudan Maviye — Marka Rengi ve Navbar/Logo Düzeltmesi

**Tarih:** 2026-08-13
**Durum:** Onaylandı, uygulanıyor.

## Bağlam

`templates/index.html`'in mevcut (v1.12) tasarımı krem zemin + terracotta turuncu (`#DD5C22`) vurgu rengi kullanıyor (bkz. `CLAUDE.md` Bölüm 1). Logo da 2026-08-10'da orijinal mavi/iki-tonlu sürümlerden tamamen turuncu bir kalkan ikonuna (`static/logo-kalkan.png`) geçmişti.

Kullanıcı geri bildirimi: turuncu tonları sevmedi, "itici" buldu. Netleştirme turunda gerçek şikayet iki somut soruna indirgendi:
1. **Navbar çok koyu** — mevcut zemin `rgba(36,26,16,0.92)` (koyu kahve).
2. **Logo küçük boyutta belirsiz** — kalkan ikonu (kafa silüeti + stetoskop + belge, ince çizgiler) 16–32px'te (favicon, navbar) okunmuyor, bir "karalama" gibi görünüyor.

Bir HTML önizleme (renk paleti + navbar önce/sonra + logonun gerçek dosyadan 16/32/28/128px render'ları) kullanıcıya gösterildi ve onaylandı ("uygula").

## Karar Verilen Kapsam

Sorularla netleştirilen nihai kapsam — **navbar + logo + sitedeki TÜM turuncu vurgular** maviye dönüyor (sadece navbar/logo değil):

### 1. Renk token'ları (`templates/index.html` `:root`)
| Token | Eski | Yeni |
|---|---|---|
| `--accent` | `#DD5C22` | `#2563EB` |
| `--accent-dark` (hover) | `#B3450F` | `#1D4ED8` |
| `--accent-soft` | `#FBE3CE` | `#DBEAFE` |
| `--accent-softer` | `#FCEEE1` | `#EFF6FF` |
| *(yeni)* `--accent-light` (koyu zeminlerde kullanılan ton) | — | `#60A5FA` (eskiden hard-code `#F3A87A`) |
| *(yeni)* `--accent-rgb` (rgba() gölge/glow için) | — | `37,99,235` |

Sitede `var(--accent...)` kullanan ~32 yer otomatik güncellenir. Ayrıca:
- 14 yerde hard-code `rgba(221,92,34,X)` → `rgba(var(--accent-rgb),X)`
- 7 yerde hard-code `#F3A87A` → `var(--accent-light)`

**Kapsam dışı (dokunulmayacak):** krem/kağıt zemin (`--paper`), premium teklif kartının altın/amber rengi (`#FBBF24`/`#F59E0B` — ayrı bir "özel paket" sinyali, turuncu ailesinden değil), `--danger`/`--success` semantik renkleri, Türk bayrağı kırmızısı, Anthropic marka rengi (varsa).

### 2. Navbar (`templates/index.html` `.navbar` ve ilişkili kurallar)
- Zemin: `rgba(36,26,16,0.92)` (koyu kahve) → beyaz/neredeyse-beyaz, ince alt gölge/çizgiyle ayrılır.
- Doğal sonuç: `.navbar-brand` metin rengi (`#FFFFFF`) ve `.navbar-links a` rengi (`#D9CDBA`) koyu mürekkep tonlarına döner (beyaz zeminde beyaz/krem yazı görünmez).
- `.navbar-cta` zaten `var(--accent)` kullanıyor, otomatik maviye döner.

### 3. Logo/favicon/OG görseli
Aynı kavram korunuyor (kafa silüeti + stetoskop + belge, kalkan içinde), ama:
- Daha kalın/az detaylı çizgilerle, küçük boyutta (16–32px) okunacak şekilde yeniden çizilecek.
- Mavi (`#2563EB` ailesi) olacak.
- `static/logo-mark-koyu.png` (navbar), `static/favicon-32.png`, `static/og-image.png` tutarlı hale gelecek.

**Doğrulanmış risk:** Brainstorming sırasında bu ikonu basitleştirip maviye çevirmek için 2 hızlı SVG taslağı denendim, ikisi de aynı küçük-boyut okunabilirlik testinde (16/28/32px render + Chrome screenshot) başarısız oldu — hâlâ karışık görünüyorlardı. Serbest elle SVG path koordinatı tahmin etmek bu iş için güvenilir değil. Nihai ikon, görsel geri bildirim döngüsü olan bir araçla (AI logo üretim aracı veya elle vektör çizim) üretilecek ve **aynı küçük-boyut testinden geçmeden** canlıya alınmayacak. Geçmezse dürüst bir düşüş planı: navbar'da geçici olarak sadece wordmark (ikon yok), favicon eski haliyle kalır — kullanıcıya bildirilir, sessizce "kabul edilebilir" ilan edilmez.

## Test Protokolü
1. Renk token + navbar değişikliği sonrası yerel `uvicorn` ile çalıştırıp CDP (`Emulation.setDeviceMetricsOverride`) ile hem masaüstü (1440px) hem mobil (390px) tam sayfa ekran görüntüsü.
2. Yeni logo/favicon adayı varsa: aynı 16/28/32/128px render testi (bu spec'in hazırlığında kullanılan yöntemle) — geçmeden entegre edilmeyecek.
3. Mevcut testler/lint yoksa (proje otomatik test suite'i yok), manuel kontrol: SSS accordion, form, premium kart, mobil menü hâlâ çalışıyor mu (regresyon kontrolü — CLAUDE.md Bölüm 3.1).

## Deploy
Yerel doğrulama sonrası kullanıcıdan ayrı onay alınmadan production'a (`cvdoktoru.com`) push/deploy yapılmayacak — CLAUDE.md hard-stop listesi ve genel git safety protokolü gereği.
