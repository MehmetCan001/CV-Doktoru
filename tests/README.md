# 🧪 Test Rehberi

Bu klasör, CV Doktoru'nu test etmek için kullanılan örnek CV ve iş ilanlarını içerir.

## Dosyalar

- `test_cv_ornek.txt` — Tipik junior hatalarını içeren örnek CV (senin 4 yıl önceki CV'n gibi)
- `test_ilan_ornek.txt` — Junior Python Developer iş ilanı

## Test Stratejisi

### 1. Smoke Test
İlk olarak API ve prompt yapısının çalıştığını doğrula:

```bash
python -m src.main test
```

Beklenti: Claude kendini "CV Doktoru" olarak tanıtmalı, 2-3 cümleyle ne yaptığını anlatmalı.

### 2. Prompt Boyut Kontrolü
Prompt çok mu büyük? Token limitini aşıyor mu?

```bash
python -m src.main info
```

Beklenti: Toplam tahmini token sayısı 10K-15K civarında olmalı. 30K'ı aşıyorsa optimizasyon gerekir.

### 3. Tam Analiz Testi
Asıl test — gerçek bir CV analizi:

```bash
python -m src.main analyze \
  --cv tests/test_cv_ornek.txt \
  --job tests/test_ilan_ornek.txt \
  --output data/test_raporu.md
```

### Değerlendirme Kriterleri

İyi bir rapor şu özelliklere sahip olmalı:

✅ **Var olmalı:**
- Skor 100 üzerinden net bir sayı (bu CV için 25-40 arası beklenir)
- "İlk İzlenim" bölümü 4-6 cümle, mentor tonunda
- En az 3 kırmızı bayrak, her birinde önce-sonra örneği
- En az 2 güçlü nokta
- Spesifik 3-5 anahtar kelime önerisi
- Bugün yapılabilecek 3-5 somut eylem

❌ **Olmamalı:**
- "Lütfen dikkate alın" gibi mesafeli ifadeler
- Genel klişeler ("CV'nizi güncel tutun")
- "Harika!" gibi yapay iyimserlik
- Çok kısa raporlar (3 paragraflık özet işe yaramaz)
- Çok uzun, okunamayan raporlar (2000 kelime üzeri ağır gelir)

## Kendi CV'nle Test

Asıl test budur. Kendi 4 yıl önceki CV'ni `data/` klasörüne koy:

```bash
python -m src.main analyze \
  --cv data/benim_eski_cv.pdf \
  --job tests/test_ilan_ornek.txt \
  --output data/benim_raporum.md
```

Raporu oku ve şunu sor: **"Bu rapor için 49 TL öder miydim?"**

Cevap **evet** ise → ürün hazır demektir.
Cevap **hayır** ise → prompt'u iyileştirelim.
