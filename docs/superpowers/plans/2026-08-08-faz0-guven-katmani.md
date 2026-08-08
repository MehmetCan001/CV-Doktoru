# Faz 0 — Güven Katmanı Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CV Doktoru'na eksik olan resmi güven/şeffaflık katmanını eklemek — gerçek bir Gizlilik/KVKK sayfası, footer'da gerçek iletişim/gizlilik linkleri, ve "verileriniz saklanmaz" iddiasını kodda %100 doğru hale getiren bir temizlik.

**Architecture:** Mevcut proje deseni korunur — ayrı bir template engine/component sistemi yok, `templates/index.html` tek dosyalık bir sayfa, `src/server.py` bu dosyayı ham metin olarak okuyup döndürüyor (Jinja2 interpolasyonu kullanılmıyor). Yeni Gizlilik sayfası da aynı desende, ayrı bir statik HTML dosyası (`templates/gizlilik.html`) + aynı okuma deseniyle yeni bir route olarak eklenir.

**Tech Stack:** FastAPI (`src/server.py`), vanilla HTML/CSS/JS (Jinja2 kullanılmıyor — bkz. Global Constraints), Python 3.

## Global Constraints

- Şablon motoru yok: `templates/*.html` dosyaları ham metin olarak okunup `HTMLResponse` ile döndürülür (`src/server.py:74-76`). Yeni sayfa da bu deseni takip eder, `{{ }}` gibi Jinja2 sözdizimi kullanılmaz.
- Test çerçevesi yok (`requirements.txt`'de pytest yok). Doğrulama, yerel sunucuyu çalıştırıp tarayıcı/curl ile manuel kontrol şeklinde yapılır — projenin mevcut konvansiyonu budur.
- Dil: Tüm kullanıcıya görünen metin Türkçe.
- Tasarım: Mevcut CSS değişkenleri kullanılır (`--paper`, `--accent`, `--ink` vb., `templates/index.html:56-76`), yeni bir renk paleti icat edilmez.
- Dürüstlük ilkesi (CLAUDE.md Bölüm 6/11): Gizlilik metnindeki her cümle kodda karşılığı olmalı — var olmayan bir şirket unvanı, var olmayan bir garanti yazılmaz.
- İletişim e-postası: `destek@cvdoktoru.com` (kullanıcı tarafından ImprovMX ile bu oturumda kuruldu).
- Veri Sorumlusu: "Mehmet" (şahıs olarak yürütülüyor, kayıtlı şirket yok — 2026-08-08'de netleşen karar).

---

### Task 1: `data/last_report.txt` debug yazımını kaldır

**Neden:** `_run_analysis_job` şu an her analiz sonucunu tek, paylaşılan bir dosyaya (`data/last_report.txt`) yazıyor — bu, Gizlilik sayfasında yazacağımız "raporunuz diske hiç yazılmaz" iddiasını yanlış yapıyor. Bu yazma işlemi başka hiçbir yerde okunmuyor (yalnızca eski/kullanılmayan Streamlit arayüzü `src/app.py` okuyor, üretimde çalışan `server.py` değil) ve zaten `try/except: pass` ile sarılı, yani hiçbir işlevsel davranış buna bağımlı değil. Kaldırınca "veriniz sunucuda dosya olarak hiç saklanmaz" iddiası istisnasız doğru olur.

**Files:**
- Modify: `src/server.py:136-156` (`_run_analysis_job` fonksiyonu)

**Interfaces:**
- Consumes: yok (saf silme işlemi)
- Produces: `_run_analysis_job` davranışı değişmiyor — sadece dosyaya yazma yan etkisi kaldırılıyor, `_jobs[job_id]["report"]` üzerinden rapor teslimi aynı şekilde çalışmaya devam ediyor.

- [ ] **Step 1: Debug yazma bloğunu sil**

`src/server.py` içinde şu bloğu:

```python
def _run_analysis_job(job_id: str, cv_text: str, job_text: str) -> None:
    doctor = CVDoctor()
    try:
        report = doctor.analyze(cv_text, job_text)
        report = _round_score(report)
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = f"Analiz hatası ({type(e).__name__}): {e}"
        return

    try:
        report_file = config.DATA_DIR / "last_report.txt"
        report_file.parent.mkdir(exist_ok=True)
        report_file.write_text(report, encoding="utf-8")
    except Exception:
        pass

    with _jobs_lock:
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["report"] = report
```

şu şekilde değiştir:

```python
def _run_analysis_job(job_id: str, cv_text: str, job_text: str) -> None:
    doctor = CVDoctor()
    try:
        report = doctor.analyze(cv_text, job_text)
        report = _round_score(report)
    except Exception as e:
        with _jobs_lock:
            _jobs[job_id]["status"] = "error"
            _jobs[job_id]["error"] = f"Analiz hatası ({type(e).__name__}): {e}"
        return

    with _jobs_lock:
        _jobs[job_id]["status"] = "done"
        _jobs[job_id]["report"] = report
```

- [ ] **Step 2: `config` importunun hâlâ kullanıldığını doğrula**

`src/server.py` içinde `config` modülü `TEMPLATES_DIR = config.PROJECT_ROOT / "templates"` satırında (dosyanın başında) hâlâ kullanılıyor, bu yüzden import satırını silme — sadece `_run_analysis_job` içindeki kullanımı kaldırıldı.

Kontrol et: `grep -n "config\." src/server.py` çalıştır, en az bir kullanım (TEMPLATES_DIR/STATIC_DIR tanımları) görünmeli.

- [ ] **Step 3: Manuel doğrulama — sunucuyu başlat ve dosyanın oluşmadığını gör**

```bash
# Varsa eski last_report.txt'yi sil (temiz test için)
rm -f data/last_report.txt

# Sunucuyu başlat
uvicorn src.server:app --host 0.0.0.0 --port 8501
```

Tarayıcıdan `http://localhost:8501/` adresine git, gerçek bir CV metni + iş ilanı ile analiz çalıştır, tamamlanmasını bekle. Ardından:

```bash
ls data/last_report.txt
```

Beklenen: `No such file or directory` (dosya oluşmamalı). Eskiden bu dosya oluşuyordu; artık oluşmuyor olması değişikliğin doğru çalıştığının kanıtı.

- [ ] **Step 4: Commit**

```bash
git add src/server.py
git commit -m "fix: last_report.txt debug yazımını kaldır — veri saklanmaz iddiası artık istisnasız doğru"
```

---

### Task 2: Gizlilik/KVKK sayfası ve route'u ekle

**Neden:** Şu an sitede hiçbir Gizlilik/KVKK sayfası yok (`src/` içinde bu terimler için sıfır eşleşme doğrulandı). CVCIM gibi güvenilir rakiplerin sahip olduğu, cvanaliz.com'un ise doldurulmamış bir şablonla berbat ettiği bu belge, Faz 0'ın en somut çıktısı.

**Files:**
- Create: `templates/gizlilik.html`
- Modify: `src/server.py` (yeni route, `index()` fonksiyonunun hemen altına)

**Interfaces:**
- Consumes: yok
- Produces: `GET /gizlilik` → `200 text/html`, footer'daki (Task 3) `/gizlilik` linkinin hedefi budur.

- [ ] **Step 1: `templates/gizlilik.html` dosyasını oluştur**

```html
<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gizlilik ve KVKK Aydınlatma Metni — CV Doktoru</title>
<meta name="description" content="CV Doktoru'nda hangi verilerinizin işlendiğini, ne kadar süre saklandığını ve KVKK kapsamındaki haklarınızı öğrenin.">
<meta name="robots" content="index, follow">
<link rel="canonical" href="https://cvdoktoru.com/gizlilik">
<link rel="icon" type="image/png" href="/static/logo.png?v=2">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*, *::before, *::after { box-sizing: border-box; }
:root {
    --bg: #FBF5EB;
    --paper: #FFFDF8;
    --ink: #271F16;
    --ink-soft: #6B5D4B;
    --ink-faint: #9C8E78;
    --line: #E7D9BF;
    --accent: #DD5C22;
    --accent-dark: #B3450F;
}
body {
    margin: 0;
    background: var(--bg);
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: var(--ink);
    line-height: 1.65;
}
.legal-container { max-width: 720px; margin: 0 auto; padding: 3rem 1.5rem 4rem; }
.legal-back { display: inline-block; margin-bottom: 2rem; color: var(--ink-soft); text-decoration: none; font-size: 0.9rem; font-weight: 600; }
.legal-back:hover { color: var(--accent-dark); }
h1 { font-family: 'Fraunces', Georgia, serif; font-size: 1.9rem; margin: 0 0 0.4rem; }
.legal-updated { color: var(--ink-faint); font-size: 0.85rem; margin-bottom: 2.2rem; }
h2 { font-family: 'Fraunces', Georgia, serif; font-size: 1.25rem; margin: 2.2rem 0 0.8rem; color: var(--ink); }
p { margin: 0 0 1rem; color: var(--ink-soft); }
strong { color: var(--ink); }
ul { margin: 0 0 1rem; padding-left: 1.3rem; color: var(--ink-soft); }
li { margin-bottom: 0.4rem; }
a { color: var(--accent-dark); }
.legal-contact-box { background: var(--paper); border: 1px solid var(--line); border-radius: 12px; padding: 1.2rem 1.4rem; margin-top: 2.5rem; }
.legal-contact-box a { font-weight: 700; }
</style>
</head>
<body>
<div class="legal-container">
  <a href="/" class="legal-back">← Ana Sayfaya Dön</a>

  <h1>Gizlilik ve KVKK Aydınlatma Metni</h1>
  <div class="legal-updated">Son güncelleme: 8 Ağustos 2026</div>

  <h2>Veri Sorumlusu</h2>
  <p>CV Doktoru (cvdoktoru.com), Mehmet tarafından şahıs olarak yürütülen bir hizmettir; kayıtlı bir şirket bulunmamaktadır. 6698 sayılı Kişisel Verilerin Korunması Kanunu ("KVKK") kapsamında veri sorumlusu Mehmet'tir. Sorularınızı veya taleplerinizi <a href="mailto:destek@cvdoktoru.com">destek@cvdoktoru.com</a> adresine iletebilirsiniz.</p>

  <h2>Hangi Verileri İşliyoruz, Ne Kadar Süre Saklıyoruz</h2>
  <p><strong>CV'niz ve iş ilanı metni:</strong> Analiz üretmek için Anthropic'in Claude yapay zeka modeline iletilir (bkz. "Yurt Dışı Aktarım" bölümü). Analiz raporunuz, tarayıcınıza gösterilebilmesi için en fazla 30 dakika sunucu belleğinde (RAM) tutulur; bu sürenin sonunda otomatik olarak silinir. CV'niz veya raporunuz hiçbir zaman dosya olarak diske yazılmaz, bir veritabanında saklanmaz.</p>
  <p><strong>IP adresiniz:</strong> Kötüye kullanımı önlemek amacıyla (günlük 3 ücretsiz analiz sınırı) IP adresiniz yalnızca o gün için sunucuda tutulur; her yeni istekte önceki günlere ait kayıtlar otomatik olarak silinir.</p>
  <p><strong>Sayfa ziyaretleri ve buton tıklamaları:</strong> Ürünü iyileştirmek için anonim kullanım istatistiği tutuyoruz. Ham IP adresiniz hiçbir zaman diske yazılmaz — yalnızca tuzlanmış (geri döndürülemez şekilde şifrelenmiş) bir özet tutulur, bu özet sizi kimliklendirmek için kullanılamaz. Google Analytics, Facebook Pixel gibi üçüncü taraf bir analitik veya reklam servisi kullanılmaz.</p>
  <p><strong>E-posta adresiniz:</strong> Yalnızca "Derin Analiz Paketi" bekleme listesine kendi isteğinizle kaydolursanız e-posta adresiniz ve kayıt tarihi saklanır. Bu kaydın silinmesini istediğiniz her an <a href="mailto:destek@cvdoktoru.com">destek@cvdoktoru.com</a> üzerinden talep edebilirsiniz.</p>

  <h2>Neden İşliyoruz</h2>
  <ul>
    <li>CV analizi hizmetini sunmak (KVKK m.5/2 — talebinizin ifası),</li>
    <li>Hizmetin kötüye kullanılmasını önlemek (meşru menfaat),</li>
    <li>Ürünü iyileştirmek için anonim, kimliksizleştirilmiş kullanım verisi toplamak (meşru menfaat),</li>
    <li>Bekleme listesine kaydolan kullanıcılarla iletişim kurmak (açık rızanız — e-posta bırakarak verdiğiniz rıza).</li>
  </ul>

  <h2>Yurt Dışı Aktarım</h2>
  <p>CV'niz ve iş ilanı metni, analiz üretmek amacıyla ABD merkezli Anthropic'in Claude API'sine iletilir. Bu aktarım yalnızca analiz talebiniz süresince gerçekleşir; yukarıda açıklandığı gibi kalıcı bir kopya bizim tarafımızda tutulmaz.</p>

  <h2>KVKK Kapsamındaki Haklarınız</h2>
  <p>KVKK'nın 11. maddesi uyarınca; verilerinizin işlenip işlenmediğini öğrenme, işleme amacını öğrenme, yurt içinde/yurt dışında aktarıldığı tarafları bilme, eksik veya yanlış işlenmişse düzeltilmesini isteme, silinmesini/yok edilmesini isteme ve bu işlemlerin aktarıldığı taraflara bildirilmesini isteme haklarına sahipsiniz. Bu haklarınızı kullanmak için <a href="mailto:destek@cvdoktoru.com">destek@cvdoktoru.com</a> adresinden bize ulaşabilirsiniz; talepler kanun gereği en geç 30 gün içinde ücretsiz olarak sonuçlandırılır.</p>

  <div class="legal-contact-box">
    Sorularınız için: <a href="mailto:destek@cvdoktoru.com">destek@cvdoktoru.com</a>
  </div>
</div>
</body>
</html>
```

- [ ] **Step 2: `/gizlilik` route'unu ekle**

`src/server.py` içinde `index()` fonksiyonunun hemen altına (satır 76-77 arası) şunu ekle:

```python
@app.get("/", response_class=HTMLResponse)
def index():
    return (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")


@app.get("/gizlilik", response_class=HTMLResponse)
def gizlilik():
    return (TEMPLATES_DIR / "gizlilik.html").read_text(encoding="utf-8")
```

(Yalnızca `index()` fonksiyonundan sonra yeni `gizlilik()` fonksiyonu ekleniyor, `index()`'in kendisi değişmiyor.)

- [ ] **Step 3: Manuel doğrulama**

```bash
uvicorn src.server:app --host 0.0.0.0 --port 8501
```

Başka bir terminalde:

```bash
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8501/gizlilik
```

Beklenen: `200`. Ardından tarayıcıda `http://localhost:8501/gizlilik` adresini aç, sayfanın düzgün render olduğunu (font, renkler, "Ana Sayfaya Dön" linki çalışıyor mu) gözle kontrol et.

- [ ] **Step 4: Commit**

```bash
git add templates/gizlilik.html src/server.py
git commit -m "feat: Gizlilik/KVKK aydınlatma metni sayfası ekle (/gizlilik)"
```

---

### Task 3: `index.html`'e güven sinyallerini ekle (footer linkleri + gerçek destek e-postası)

**Neden:** Footer şu an tek satır, hiçbir İletişim/Gizlilik linki yok. Ayrıca SSS bölümünün altındaki destek notu ("Yakında buradan destek ekibimize de ulaşabileceksiniz") önceki bir oturumda gerçek bir e-posta olmadığı için nötr bırakılmıştı (bkz. `memory/checkpoint-son.md`) — artık `destek@cvdoktoru.com` var, bunu gerçek bir linke çeviriyoruz.

**Files:**
- Modify: `templates/index.html` (CSS: `.footer-note` tanımının yanı, satır ~437; HTML: footer bloğu satır ~777-780; FAQ destek notu satır ~777)

**Interfaces:**
- Consumes: Task 2'de eklenen `/gizlilik` route'u
- Produces: yok (uç nokta, başka hiçbir task buna bağımlı değil)

- [ ] **Step 1: Footer linkleri için CSS ekle**

`templates/index.html` içinde şu satırı bul:

```css
.footer-note { text-align: center; color: var(--ink-faint); font-size: 0.82rem; padding: 2rem 0 1rem; }
```

Hemen altına ekle:

```css
.footer-note { text-align: center; color: var(--ink-faint); font-size: 0.82rem; padding: 2rem 0 1rem; }

.footer-links { display: flex; align-items: center; justify-content: center; gap: 0.6rem; padding-top: 1.5rem; font-size: 0.82rem; }
.footer-links a { color: var(--ink-soft); text-decoration: none; font-weight: 600; }
.footer-links a:hover { color: var(--accent-dark); }
.footer-links span { color: var(--ink-faint); }
```

- [ ] **Step 2: Footer HTML'ini güncelle**

Şu bloğu:

```html
  <div class="footer-note">CV Doktoru — Türkiye'nin iş ilanına özel CV analiz aracı</div>
</div>
```

şu şekilde değiştir:

```html
  <div class="footer-links">
    <a href="/gizlilik">Gizlilik &amp; KVKK</a>
    <span aria-hidden="true">·</span>
    <a href="mailto:destek@cvdoktoru.com">İletişim</a>
  </div>
  <div class="footer-note">CV Doktoru — Türkiye'nin iş ilanına özel CV analiz aracı</div>
</div>
```

- [ ] **Step 3: FAQ destek notunu gerçek mailto linkine çevir**

Şu satırı:

```html
    <div class="faq-support-note">Aradığınız cevabı bulamadınız mı? Yakında buradan destek ekibimize de ulaşabileceksiniz.</div>
```

şu şekilde değiştir:

```html
    <div class="faq-support-note">Aradığınız cevabı bulamadınız mı? <a href="mailto:destek@cvdoktoru.com">destek@cvdoktoru.com</a> adresinden bize ulaşabilirsiniz.</div>
```

- [ ] **Step 4: `.faq-support-note a` için link stili ekle**

`templates/index.html:287` içinde şu satırı bul:

```css
.faq-support-note { text-align: center; margin-top: 2rem; font-size: 0.85rem; color: var(--ink-faint); }
```

Hemen altına ekle:

```css
.faq-support-note { text-align: center; margin-top: 2rem; font-size: 0.85rem; color: var(--ink-faint); }
.faq-support-note a { color: var(--accent-dark); font-weight: 700; text-decoration: none; }
.faq-support-note a:hover { text-decoration: underline; }
```

- [ ] **Step 5: Manuel doğrulama**

```bash
uvicorn src.server:app --host 0.0.0.0 --port 8501
```

Tarayıcıda `http://localhost:8501/` aç:
1. Sayfanın en altına in, footer'da "Gizlilik & KVKK" ve "İletişim" linklerinin göründüğünü doğrula.
2. "Gizlilik & KVKK" linkine tıkla, `/gizlilik` sayfasının açıldığını doğrula.
3. "İletişim" linkine tıkla, mail istemcisinin `destek@cvdoktoru.com` ile açılmaya çalıştığını doğrula (gerçek mail göndermene gerek yok, sadece `mailto:` linkinin tetiklendiğini gör).
4. SSS bölümüne in, en alttaki destek notunda artık gerçek bir link olduğunu ve tıklanabilir olduğunu doğrula.
5. Mobil görünümü de kontrol et (CLAUDE.md kuralı: native headless Chrome screenshot yerine CDP `Emulation.setDeviceMetricsOverride({mobile:true})` kullan veya gerçek cihazda bak) — footer linklerinin mobilde de okunabilir/tıklanabilir boyutta olduğunu doğrula.

- [ ] **Step 6: Commit**

```bash
git add templates/index.html
git commit -m "feat: footer'a Gizlilik/İletişim linkleri ekle, SSS destek notunu gerçek e-postaya çevir"
```

---

## Faz 0 Tamamlanma Kriteri

Tüm task'lar tamamlandığında:
- [ ] `data/last_report.txt` artık hiçbir analizde oluşmuyor.
- [ ] `/gizlilik` sayfası canlı ve doğru render oluyor.
- [ ] Footer'da Gizlilik ve İletişim linkleri var, ikisi de çalışıyor.
- [ ] SSS destek notu gerçek bir mailto linkine sahip.
- [ ] Tasarım tasarım dosyasındaki (`docs/superpowers/specs/2026-08-08-rakip-farklilasma-stratejisi-design.md`) "Faz 0 — Güven Katmanı" bölümündeki üç madde (footer, Gizlilik sayfası, şeffaflık) karşılanmış oluyor — üçüncü madde ("Nasıl Analiz Ediyoruz" bloğu) ayrı bir bölüm yerine Gizlilik sayfasının "Hangi Verileri İşliyoruz" + mevcut SSS'teki "Bu analizi yapay zeka mı yapıyor" sorusu üzerinden karşılanıyor (bkz. Task 2 gerekçesi — mevcut SSS içeriğiyle neredeyse birebir çakışan ayrı bir bölüm eklemek tekrar/şablon hissi yaratırdı, CLAUDE.md Bölüm 1 tasarım felsefesiyle çelişirdi).

Bundan sonraki adım (Faz 1 — Dağıtım) ayrı bir brainstorming/spec turunda ele alınacak (bkz. tasarım dokümanı).
