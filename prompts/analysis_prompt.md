# CV Analiz Prompt'u

Bu, kullanıcı CV + iş ilanı verdiğinde çalıştırılacak ana prompt'tur.
`{cv_text}` ve `{job_ad}` placeholder'ları Python tarafından doldurulur.

---

Aşağıda bir CV ve bir iş ilanı var. CV'yi iş ilanına göre kapsamlı şekilde analiz et.

Sistem prompt'unda tanımlandığın "CV Doktoru" karakteriyle, samimi-mentor tonuyla, ama profesyonel kalarak konuş.

Çıktıyı TAM olarak aşağıdaki formatta üret. Bölüm başlıkları değişmesin. Markdown formatı kullan.

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

CV'de iş ilanına göre **somut sorun** yaratan 3-5 şey. Her biri için:

### 1. [Sorunun başlığı]
**Şu an CV'de:** "[CV'den birebir alıntı]"

**Sorun:** Neden bu sorun. 1-2 cümle.

**Önerilen yeni hali:** "[Geliştirilmiş cümle/bölüm]"

### 2. [Bir sonraki sorun]
... (aynı formatla devam)

(En az 3, en fazla 5 madde)

---

## ✅ GÜÇLÜ NOKTALAR

CV'de **gerçekten iyi yapılmış** 2-3 şey. Yapay iyimserlik değil, gerçekten övgüye değer şeyleri yaz.

### 1. [Güçlü nokta]
Ne, neden iyi, daha da öne çıkarmak için ne yapılabilir.

(2-3 madde)

---

## 🎯 İŞ İLANINA UYUM

İş ilanında geçen ama CV'de **eksik veya az vurgulanmış** anahtar kelimeler ve yetkinlikler.

### Eksik veya zayıf anahtar kelimeler:
- **[anahtar kelime]**: İlanda neden istendiği, sende var mı, varsa nasıl ekleyeceğin (somut cümle örneği).
- **[anahtar kelime]**: ...
- (3-5 madde)

### Eksik bölümler:
İş ilanı X bekliyor ama CV'de bu hiç yok. Örnek: GitHub linki, kişisel proje, belirli bir sertifika.

---

## 💡 SOMUT EYLEMLER (1 GÜN İÇİNDE YAPABİLECEKLERİN)

Kullanıcı bu raporu okuduktan sonra **bugün/yarın** CV'sinde yapması gereken net işler. Öncelik sırasıyla.

1. **[Eylem 1]** — Tahmini süre: X dakika. Bunu yaparsa CV'si Y açıdan güçlenir.
2. **[Eylem 2]** — ...
3. **[Eylem 3]** — ...
(En az 3, en fazla 5 eylem)

---

## 🌱 ORTA VADELİ TAVSİYELER (1-3 AY)

CV'yi geliştirmek için daha uzun vadeli işler. Örnek:
- Belirli bir sertifika almak
- Bir kişisel proje yapmak ve GitHub'a koymak
- LinkedIn'i güncellemek ve içerik üretmek
- Belirli bir online kurs

Her birinin **neden** ve **somut nasıl** kısmını yaz.

---

## 📝 SON SÖZ (MENTORDAN AÇIK KONUŞMA)

Kullanıcıya doğrudan, mentor gibi konuş. 3-5 cümle. Bu CV'nin nereye gidebileceği, kullanıcının gerçek potansiyeli, motivasyon ama abartısız.

**Örnek ton:** "Şunu bil ki, bu CV'yi bugün yazsan da yarın yazsan da bir hafta sonra yazsan da ilk 3-4 düzeltmeyi yaparsan çok farklı bir izlenim bırakacak. Asıl mesele bu raporu okuyup kapatmak değil, [spesifik 1-2 iş] yapmak. Sen yapabilirsin çünkü [CV'den gerçek bir güçlü şeye atıf]."

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
