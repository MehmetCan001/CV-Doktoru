# 🩺 CV Doktoru

> Yeni mezunların CV'lerini iş ilanlarına göre analiz eden, "abi/abla mentor" tonunda dürüst geri bildirim veren AI asistanı.

## 💡 Proje Felsefesi

**Kullanıcı sorunu:** "4 yıl sonra eski CV'me bakınca ne yazmışım diyorum" duygusu. Sen şu an o farkındalığı kazandın — başkaları henüz kazanmadı.

**Çözüm:** Mezuna o "4 yıl sonraki bakış"ı şimdi vermek. AI sayesinde anlık, kişiselleştirilmiş, dürüst.

**Hedef kitle (ilk versiyon):** Türkiye'de yeni mezun ve junior pozisyon arayanlar. Başlangıçta teknoloji/yazılım odaklı, sonra genişler.

**Fiyat:** 49 TL tek seferlik analiz.

## 📁 Proje Yapısı

```
cv-doktoru/
├── README.md                    ← Bu dosya
├── requirements.txt             ← Python bağımlılıkları
├── .env.example                 ← API key şablonu
├── .gitignore
│
├── prompts/                     ← Claude'un "becerileri" — kalbi burası
│   ├── system_prompt.md         ← Ana karakter (CV uzmanı kimliği)
│   ├── analysis_prompt.md       ← Analiz formatı şablonu
│   └── examples/                ← Few-shot örnekler
│       ├── ornek_1_yazilim.md   ← Yazılım mezunu örneği
│       └── ornek_2_pazarlama.md ← Pazarlama mezunu örneği
│
├── knowledge/                   ← Türk iş kültürü bilgi tabanı
│   ├── turk_is_kulturu.md       ← İşverenlerin ne aradığı
│   ├── cv_yaygin_hatalar.md     ← Sık yapılan 30 hata
│   └── sektor_anahtar_kelimeler.md
│
├── src/                         ← Python kodu
│   ├── __init__.py
│   ├── config.py                ← Ayarlar
│   ├── pdf_reader.py            ← PDF'den metin çekme
│   ├── analyzer.py              ← Claude API çağrısı
│   ├── prompt_loader.py         ← Prompt dosyalarını yükleme
│   └── main.py                  ← CLI test arayüzü
│
├── tests/                       ← Test CV'leri
│   ├── README.md                ← Test rehberi
│   └── test_cv_ornek.txt        ← Örnek test CV (senin eski CV gibi)
│
└── data/                        ← Çalıştığında üretilen veriler
    └── .gitkeep                 ← (raporlar buraya kaydedilir)
```

## 🎯 Geliştirme Aşamaları

**Aşama 1 (şu an):** Prompt mühendisliği. Komutsuz, sadece Claude'a "kişiliği" öğret.
**Aşama 2:** PDF okuyucu + CLI test arayüzü.
**Aşama 3:** Streamlit web arayüzü.
**Aşama 4:** Manuel ödeme + ilk müşteriler.
**Aşama 5:** Otomatik ödeme + ölçek.

## 🚀 Hızlı Başlangıç

```bash
# 1. Sanal ortam
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Paketler
pip install -r requirements.txt

# 3. .env oluştur
cp .env.example .env
# .env'i aç, ANTHROPIC_API_KEY ekle

# 4. İlk testi çalıştır
python -m src.main
```

## 📝 İlk Görev: Prompt'u Test Et

Kod yazmadan önce, `prompts/system_prompt.md` ve `prompts/analysis_prompt.md` dosyalarındaki Claude'un "kişiliğini" oku. Eksik veya değiştirmek istediğin yerleri belirle.

Sonra Claude.ai'ye git, system_prompt'u yapıştır, kendi eski CV'nle test et. Çıktıyı beğenirsen kod yazmaya geçeriz.
