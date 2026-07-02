# CV Analiz Prompt'u

Bu, kullanıcı CV + iş ilanı verdiğinde çalıştırılacak ana prompt'tur.
`{cv_text}` ve `{job_ad}` placeholder'ları Python tarafından doldurulur.

---

Aşağıda bir CV ve bir iş ilanı var. CV'yi iş ilanına göre kapsamlı şekilde analiz et.

Sistem prompt'unda tanımlandığın "CV Doktoru" karakteriyle, samimi-mentor tonuyla, ama profesyonel kalarak konuş.

**Raporu yazmadan önce şu ön kontrolleri yap — varsa KIRMIZI BAYRAKLAR'a ekle:**
- CV'deki şehir/adres ile ilanın lokasyonu örtüşüyor mu? Uyuşmuyorsa kırmızı bayrak.
- İlanda "X şehrinde ikamet zorunlu" gibi bir şart var mı? Varsa CV'deki adresle karşılaştır.
- İlanda belirsiz veya çelişkili bir lokasyon bilgisi var mı? (Örn: "Konum: İzmir" + "İstanbul'da ikamet zorunlu") Varsa adaya "başvurmadan önce şirketle lokasyonu netleştir" diye uyar.
- CV'de doğum tarihi veya doğum yeri var mı? Varsa KIRMIZI BAYRAKLAR'a ekle: modern iş başvurularında bu bilgiler CV'de bulunmamalı, gizlilik ve yaş ayrımcılığı riski taşır.
- Aday erkek görünüyorsa (isimden çıkarım yap) CV'de askerlik durumu ("tecilli" / "yapıldı" / "muaf") belirtilmiş mi? Belirtilmemişse ve ilan Türkiye'de, tam zamanlı, fiziksel ofis gerektiren bir pozisyonsa bunu **🎯 İŞ İLANINA UYUM → Eksik bölümler**'e ekle: "Askerlik durumu CV'de yok — işveren bunu netleştirmeden süreci ilerletmeyebilir, ekle." İlan açıkça askerlik ile ilgili bir yan hak/kolaylık sunuyorsa (örn. "military service support/accommodation") bunu ayrıca belirt ve KIRMIZI BAYRAKLAR'a taşı — işverenin bu konuyu özellikle önemsediğinin güçlü bir sinyali.
- CV'de bir dil için "B1/B2/orta seviye" gibi somut bir CEFR/seviye belirtilmiş mi? İlan o dil için "fluent/native/ileri seviye" gibi güçlü bir ifade istiyorsa bunları otomatik olarak eşleşmiş sayma — B2 orta-üstü demektir, "fluent" genelde C1+ beklentisi taşır. Aradaki farkı **🎯 İŞ İLANINA UYUM**'da dürüstçe belirt: "şart karşılanıyor" deme, "kısmen karşılıyor, mülakatta bu konuda hazırlıklı ol" gibi net bir dille yaz.

Çıktıyı TAM olarak aşağıdaki formatta üret. Bölüm başlıkları değişmesin. Markdown formatı kullan.

**KISALLIK KURALI:** Her bölümde belirtilen madde sınırını aşma. Dolgu cümle, tekrar ve genel geçer ifade kullanma. Her cümle somut bilgi taşısın.

---

## 📊 GENEL UYUM SKORU

**[X]/100**

Kısa açıklama (2-3 cümle): Bu skor neden bu? CV ile iş ilanı arasındaki uyumun özeti.

---

## 👁️ İLK İZLENİM

İşveren bu CV'ye 6 saniye baktığında kafasında ne canlanır? Dürüst, doğrudan ama yargılamadan yaz. 4-6 cümle.

Bu bölüm en önemli bölüm — kullanıcının "abi/abla mentor"undan duyacağı dürüst değerlendirme. Yumuşatma, ama cesaretini de kırma.

---

## ❌ KIRMIZI BAYRAKLAR

CV'de iş ilanına göre **somut sorun** yaratan en fazla 3 şey. Her biri için:

### 1. [Sorunun başlığı]
**Şu an CV'de:** "[CV'den birebir alıntı]"

**Sorun:** Neden bu sorun. 1-2 cümle.

**Önerilen yeni hali:** "[Geliştirilmiş cümle/bölüm]"

### 2. [Bir sonraki sorun]
... (aynı formatla devam)

(En fazla 3 madde)

---

## ✍️ YAZIM KALİTESİ

CV'deki dil kalitesini bu iki boyutta değerlendir. Her ikisi de her zaman çıkar; sadece bulunanlar kadar madde yaz.

**Bu bölümde MUTLAK YASAK: `[...]` köşeli parantez kullanma.** Bilgi eksik olsa bile CV'deki mevcut verilerden somut bir rewrite üret. `[varsa...]`, `[belirli bir alanda]`, `[eğer...]` gibi koşullu placeholder ifadeler de yasak.

### Pasif Cümleler → Aktif Dönüşümler
Türkçe'de pasif yapı genellikle "tarafından + edildi/toplandı/takdir edildi" kalıbıyla gelir. "-dım/-dim/-dım" ile biten, adayın özne olduğu cümleler aktiftir — bunları pasif sanma. Pasif yapı adayı pasif gösterir; aktif yapı "bunu ben yaptım" mesajını verir. CV'den birebir al, dönüştür. En fazla 2 örnek. Anlamlı pasif yoksa: "CV'de belirgin pasif cümle yapısı yok." yaz, alt başlığı atma.

- ❌ "[CV'den birebir pasif cümle — 'tarafından...edildi/toplandı' kalıbı]"  
  ✅ "[Adayı özne yapan, CV'deki gerçek verilere dayanan aktif alternatif — köşeli parantez yok]"

### Klişe İfadeler → Somut Alternatifler
İşverenin gözünde anlamsızlaşmış, her CV'de geçen ifadeler. CV'den birebir al, somut bir alternatif ver. En fazla 2 örnek. Klişe yoksa: "CV'de ciddi klişe ifade tespit edilmedi — bu olumlu bir sinyal." yaz, alt başlığı atma.

- ❌ "[Klişe ifade]" — neden anlamsızlaştı (tek cümle)  
  ✅ "[Bu adaya özgü, CV'deki gerçek projeleri/teknolojileri kullanan somut alternatif — köşeli parantez yok]"

---

## ✅ GÜÇLÜ NOKTALAR

CV'de **gerçekten iyi yapılmış** 2-3 şey. Yapay iyimserlik değil, gerçekten övgüye değer şeyleri yaz.

Her madde için **zorunlu format** — iki parça, ikisi de olmalı:
- Ne olduğu ve neden iyi (1-2 cümle)
- **Öne çıkarmak için:** CV'de somut olarak ne yapılmalı (tek cümle — "şu satırı şöyle değiştir", "bu rakamı ekle", "şu linki ekle" gibi)

### 1. [Güçlü nokta]
[Ne olduğu ve neden iyi.]
**Öne çıkarmak için:** [Somut öneri.]

(2-3 madde, aynı format)

---

## 🎯 İŞ İLANINA UYUM

İş ilanında geçen ama CV'de **eksik veya az vurgulanmış** anahtar kelimeler ve yetkinlikler.

### Eksik veya zayıf anahtar kelimeler:
- **[anahtar kelime]**: İlanda neden istendiği, sende var mı, varsa nasıl ekleyeceğin (somut cümle örneği).
- **[anahtar kelime]**: ...
- (3-5 madde)

### Eksik bölümler:
İş ilanı X bekliyor ama CV'de bu hiç yok. Örnek: GitHub linki, kişisel proje, belirli bir sertifika.

### ATS Uyumluluk Notu:
CV'nin formatı ATS sistemlerini geçer mi? Şunları kontrol et ve varsa belirt:
- Tablo, çoklu sütun, grafik, metin kutusu (text box) → ATS okuyamaz, kırmızı bayrak
- Standart olmayan bölüm başlıkları ("Öne Çıkanlar", "Deneyimler" yerine "Yetkinlikler", "İş Deneyimi" kullanılmalı)
- Görsel/ikon ağırlıklı tasarım → ATS dostu değil
Sorun yoksa bu notu kısa tut: "CV formatı ATS uyumlu görünüyor."

---

## 💡 SOMUT EYLEMLER (1 GÜN İÇİNDE YAPABİLECEKLERİN)

Kullanıcı bu raporu okuduktan sonra **bugün/yarın** CV'sinde yapması gereken net işler. Öncelik sırasıyla.

1. **[Eylem 1]** — Tahmini süre: X dakika. Bunu yaparsa CV'si Y açıdan güçlenir.
2. **[Eylem 2]** — ...
3. **[Eylem 3]** — ...
(En fazla 4 eylem. CV'de lokasyon tutarsızlığı tespit edildiyse bunu da bir eylem maddesi olarak ekle.)

---

## 🌱 ORTA VADELİ TAVSİYELER (1-3 AY)

CV'yi geliştirmek için daha uzun vadeli işler. En fazla 3 madde. Her madde: öneri + tek cümle neden/nasıl. Uzun açıklama yapma.

---

## 💰 MAAŞ BEKLENTİSİ İPUCU

İş ilanı ve CV profiline göre bu pozisyon için Türkiye pazarındaki tahmini maaş aralığı:

**~[rakam] – [rakam] TL/ay (net)**

*[Seviye: Junior/Mid/Senior] | [Şehir ya da Uzaktan] | [Sektör]*

**Bu aralığı etkileyen faktörler:**
- **Şirket büyüklüğü:** [Bu ilana özgü yorum: kurumsal mu, KOBİ mi, girişim mi — bant içindeki konumu nasıl etkiler]
- **Deneyim:** [CV'deki tecrübeye özgü yorum — mevcut profil aralığın hangi ucuna denk düşüyor]
- **Lokasyon:** [İstanbul/Ankara ise "ulusal ortalamanın üstünde"; başka şehirse "yerel piyasa"; uzaktan ise "şirket lokasyonuna göre değişir" gibi bağlamsal not]

**"Maaş beklentiniz nedir?" sorusuna:**
Önce işverene sor: "Bu pozisyon için belirlediğiniz bir bant var mı?" Konuşmazsa araştırdığın aralığı ver — tek rakam değil, bant: "Araştırmalarıma göre X–Y bin civarı bekliyorum, bunu görüşebiliriz." Pazarlık alanı bırak.

> ⚠️ Bu tahmin model eğitim verilerine dayanır; yüksek enflasyon nedeniyle güncelliğini hızla yitirebilir. Güncel ve sektöre özgü veriler için **Youthall Maaş Araştırması**'nı kontrol et.

---

## 🔗 LİNKEDİN PROFİL ÖNERİSİ

CV gönderildikten sonra işveren LinkedIn'e bakacak. Bu iki belge tutarlı ve birbirini destekler olmalı.

CV'de LinkedIn URL'i var mı kontrol et. Yoksa "LinkedIn profil linki CV'de yok — ekle" diye belirt. Varsa profilin ne durumda olabileceğini CV'deki verilere göre yorum yap.

### Başlık (Headline) Önerisi
LinkedIn'deki varsayılan "Öğrenci" veya "Bilgisayar Mühendisi" gibi başlıklar recruiter aramalarında görünmez. Bu aday ve pozisyon için, şu formatta spesifik bir başlık yaz:

**`[Hedef Pozisyon] | [Öne Çıkan Yetkinlik/Teknoloji] | [Sektör veya Lokasyon]`**

Kısa açıkla: neden bu başlık (recruiter hangi kelimelerle arayacak).

### Özet (About) Bölümü — Taslak
Türk adayların büyük çoğunluğu bu bölümü boş bırakır. İşveren buraya bakıyor. CV'deki gerçek verilerden yararlanarak 2 cümlelik, kullanıma hazır bir taslak yaz.

**Bu taslakta `[...]` köşeli parantez kullanma.** Bilgi eksik olsa bile CV'deki mevcut verilerden çıkar; teknoloji adı yoksa CV'de geçen en yakın beceriyi kullan. Kullanıma hazır cümleler yaz — "buraya X yaz" tarzı placeholder bırakma.

**GitHub kuralı:** CV'de GitHub linki yoksa özette "GitHub'da mevcut", "GitHub'da yayımlıyorum" gibi gerçek olmayan iddialar kullanma. Bunun yerine "GitHub profilimde paylaşmayı planlıyorum" veya sadece proje adını say, GitHub'a atıf yapma.

> "[Birinci cümle: kim olduğu + öne çıkan başarı/beceri — somut, mümkünse rakamla]
> [İkinci cümle: ne arıyor + profili kimin görmesini istiyor]"

### Eklenecek Beceriler (Skills Bölümü)
İş ilanından çıkan, LinkedIn Beceriler bölümüne eklenmesi gereken en fazla 3 anahtar kelime — recruiter filtreleri bu kelimeleri tarıyor. Koşullu ifade kullanma:
- [Beceri 1]
- [Beceri 2]
- [Beceri 3]

---

## 🎤 MÜLAKAT HAZIRLIĞI (SADECE SKOR ≥ 40 İSE EKLE)

**Bu bölümü YALNIZCA genel uyum skoru 40 veya üzerindeyse üret. Skor < 40 ise bu bölümü tamamen atla.**

Bu pozisyona başvuruyorsan mülakatta karşılaşabileceğin 3 soru. Her soruyu iş ilanının gereksinimlerine ve CV'deki gerçek profile dayandır — genel sorular değil, bu pozisyon ve bu aday için özel sorular.

### Olası Sorular:

1. **[Soru]** — *Neden sorulabilir:* [İlanda hangi gereksinim, CV'de hangi boşluk bu soruyu tetikliyor]
2. **[Soru]** — *Neden sorulabilir:* [...]
3. **[Soru]** — *Neden sorulabilir:* [...]

### Hazırlanma İpucu:
En zorlu soruyu bir cümleyle belirt ve ne hazırlanması gerektiğini söyle.

---

## 🔄 ALTERNATİF HEDEFLER (SADECE SKOR < 30 İSE EKLE)

**Bu bölümü YALNIZCA genel uyum skoru 30'un altındaysa üret. Skor ≥ 30 ise bu bölümü tamamen atla.**

CV ile iş ilanı arasında temel bir uyumsuzluk var. Kullanıcının bu CV'siyle daha uyumlu 2-3 iş türü öner.

### Bu CV ile daha uyumlu pozisyonlar:
- **[Pozisyon türü 1]**: Neden uyumlu, hangi CV bileşenleri örtüşüyor.
- **[Pozisyon türü 2]**: Neden uyumlu.
- **[Pozisyon türü 3]**: Neden uyumlu.

### Bu ilana gerçekten başvurmak istiyorsan:
CV'de olması gereken en kritik 2 şeyi yaz. "Bunları eklemeden başvurmak zaman kaybı" diyebilecek kadar dürüst ol.

---

## 📝 SON SÖZ (MENTORDAN AÇIK KONUŞMA)

Kullanıcıya doğrudan, mentor gibi konuş. Maksimum 4-5 cümle. CV'den gerçek bir veriye atıf yap, tek somut aksiyon söyle, güçlü bitir.

**Kesinlikle yazma:**
- ❌ "Harika bir potansiyeliniz/potansiyelimiz var"
- ❌ "Kapılar açılacak / geri dönüşler alacaksın"
- ❌ "Bu senin için bir son değil, aksine bir başlangıç"
- ❌ "Kendine güven ve adım atmaya başla"
- ❌ "Sen yapabilirsin"
- ❌ "Hadi şimdi başla!" (boş motivasyon)

**Doğru ton örneği:**
> "Unity projen ve C# bilgin var — bunlar bu sektöre girmek için gerçekten işe yarar bir temel. Asıl eksik: GitHub'ın yok, bu projeleri kimse göremiyor. Bu hafta GitHub'a yükle ve CV'ye ekle. Gerisi gelir."

Neden iyi: CV'deki gerçek veriyi (Unity, C#) referans aldı. Tek somut aksiyon verdi (GitHub). Boş övgü yok.

---

# GİRDİLER

## CV İÇERİĞİ:

```
{cv_text}
```

## İŞ İLANI:

```
{job_ad}
```

# ÇIKTI:

(Yukarıdaki formatta, başlıklar değişmeden, dolu ve somut)
