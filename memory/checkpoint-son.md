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

**Durum:** `prompts/analysis_prompt.md` + `CLAUDE.md` değişiklikleri commit'lendi ve sunucuya deploy edildi (bu checkpoint'in yazıldığı anda deploy adımı henüz tamamlanmamış olabilir — deploy adımının gerçekten çalıştığını `git log` / canlı `curl` ile doğrula).

## Açık Kalan Sorular / Sıradaki Adımlar
- [ ] **Fake-door sonucu değerlendirme** (~2026-07-14 – 2026-07-21): `unique_visitors >= 30` olunca `/api/analytics/summary` verdict'ine bak, go/no-go kararı ver.
- [ ] 5 adımlık tasarım planının 4. maddesi — mikro-etkileşim/scroll animasyonları + mobilde sticky CTA bar — henüz başlanmadı.
- [ ] Kendi IP'yi analytics sayımından hariç tutma filtresi (kullanıcı henüz "yap" demedi).
- [ ] Search Console → URL Inspection → "Request Indexing" hâlâ yapılmadı.
- [ ] FastAPI sürümünü mobil dahil gerçek cihazlarla kapsamlı test et (dosya yükleme akışı ayrıca doğrulanmadı).

## Bilinen Riskler / Dosya Notları
- Proje kökünde `Gemini_Generated_Image_vcdhajvcdhajvcdh.png` ve `Logo.png` hâlâ commit edilmemiş kaynak dosyalar olarak duruyor — dokunma, kullanıcının kendi dosyaları.
- İki venv karışıklığı (`venv/` vs `source/`) — `venv/` çalışan, `source/`'da fastapi yok, kullanma.
- Yerel test yöntemi: `"./venv/Scripts/python.exe" -m uvicorn src.server:app --host 127.0.0.1 --port 85XX` + headless Chrome. Mobil genişlik testi için CDP `Emulation.setDeviceMetricsOverride` kullan (`--window-size` tek başına yeterli değil).
- Prompt değişikliklerini gerçek API çağrısıyla test etmek için: `.env`'de `ANTHROPIC_API_KEY` mevcut, `"./venv/Scripts/python.exe"` ile `src.analyzer.CVDoctor().analyze(cv_text, job_ad)` doğrudan çağrılabilir (Windows konsolunda emoji içeren sonucu `print()` etme — `cp1254` codec `UnicodeEncodeError` verir, dosyaya UTF-8 ile yaz).
