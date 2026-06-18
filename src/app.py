"""
CV Doktoru — Streamlit Web Arayüzü

Başlatmak için:
    streamlit run src/app.py
"""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF

from src.analyzer import CVDoctor
from src.pdf_reader import extract_text_from_pdf, extract_text_from_docx

load_dotenv()

# Streamlit Cloud: secrets.toml → os.environ köprüsü (local'de .env yeterli)
try:
    for _k in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "CLAUDE_MODEL", "GEMINI_MODEL"):
        if _k in st.secrets and not os.getenv(_k):
            os.environ[_k] = st.secrets[_k]
except Exception:
    pass

# ── Sayfa ayarları ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CV Doktoru — İş İlanına Özel CV Analizi",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Genel */
    [data-testid="stAppViewContainer"] {
        background: #f5f7fa;
    }
    [data-testid="stHeader"] { background: transparent; }
    .block-container { padding-top: 0 !important; max-width: 1100px; }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 60%, #0f3460 100%);
        border-radius: 0 0 32px 32px;
        padding: 3.5rem 2rem 3rem 2rem;
        text-align: center;
        margin-bottom: 2rem;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255,255,255,0.12);
        color: #a8d8ea;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        padding: 0.35rem 1rem;
        border-radius: 50px;
        margin-bottom: 1.2rem;
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 900;
        color: #ffffff;
        line-height: 1.15;
        margin-bottom: 1rem;
    }
    .hero h1 span { color: #4fc3f7; }
    .hero p {
        font-size: 1.15rem;
        color: #b0bec5;
        max-width: 600px;
        margin: 0 auto 2rem auto;
        line-height: 1.7;
    }

    /* İstatistikler */
    .stats-bar {
        display: flex;
        justify-content: center;
        gap: 3rem;
        flex-wrap: wrap;
        margin-top: 1.5rem;
    }
    .stat-item { text-align: center; }
    .stat-number {
        font-size: 2rem;
        font-weight: 900;
        color: #4fc3f7;
        display: block;
    }
    .stat-label {
        font-size: 0.82rem;
        color: #78909c;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Nasıl çalışır */
    .how-it-works {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    }
    .how-title {
        text-align: center;
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1.5rem;
        letter-spacing: 0.5px;
    }
    .steps {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0;
        flex-wrap: wrap;
    }
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        flex: 1;
        min-width: 160px;
        padding: 0 1rem;
    }
    .step-icon {
        width: 56px; height: 56px;
        background: linear-gradient(135deg, #1a1a2e, #0f3460);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 4px 12px rgba(15,52,96,0.25);
    }
    .step-title {
        font-weight: 700;
        font-size: 0.9rem;
        color: #1a1a2e;
        margin-bottom: 0.25rem;
    }
    .step-desc { font-size: 0.8rem; color: #78909c; }
    .step-arrow {
        font-size: 1.4rem;
        color: #4fc3f7;
        padding: 0 0.5rem;
        margin-bottom: 2rem;
    }

    /* Fark kartı */
    .diff-card {
        background: linear-gradient(135deg, #e8f5e9, #f1f8e9);
        border: 1.5px solid #a5d6a7;
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        margin-bottom: 2rem;
    }
    .diff-card-title {
        font-weight: 800;
        font-size: 0.95rem;
        color: #2e7d32;
        margin-bottom: 0.5rem;
    }
    .diff-items { display: flex; gap: 1.5rem; flex-wrap: wrap; }
    .diff-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.87rem;
        color: #388e3c;
        font-weight: 600;
    }

    /* Form kartı */
    .form-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        margin-bottom: 1.5rem;
    }
    .form-label {
        font-weight: 700;
        font-size: 1rem;
        color: #1a1a2e;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* Analiz butonu */
    .stButton > button {
        background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%) !important;
        color: white !important;
        font-size: 1.1rem !important;
        font-weight: 800 !important;
        padding: 0.85rem 2rem !important;
        border-radius: 12px !important;
        border: none !important;
        box-shadow: 0 6px 20px rgba(15,52,96,0.35) !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button:hover {
        box-shadow: 0 8px 25px rgba(15,52,96,0.5) !important;
        transform: translateY(-1px) !important;
    }

    /* Rapor kutusu */
    .report-container {
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06);
        border-left: 5px solid #4fc3f7;
        margin-bottom: 1.5rem;
    }
    .report-header {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 1.5rem;
    }
    .report-header h2 {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1a1a2e;
        margin: 0;
    }
    .report-badge {
        background: #e3f2fd;
        color: #1565c0;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        letter-spacing: 0.5px;
    }

    /* Güven rozetleri */
    .trust-bar {
        display: flex;
        justify-content: center;
        gap: 2.5rem;
        flex-wrap: wrap;
        padding: 1.5rem 0;
        margin-top: 1rem;
    }
    .trust-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.83rem;
        color: #78909c;
        font-weight: 600;
    }
    .trust-icon { font-size: 1.1rem; }

    /* Tüm input alanları için global renk düzeltmesi */
    textarea, input, [data-testid="stTextArea"] textarea,
    .stTextArea textarea, div[data-baseweb="textarea"] textarea {
        border-radius: 10px !important;
        border: 1.5px solid #e0e0e0 !important;
        font-size: 0.91rem !important;
        background-color: #ffffff !important;
        color: #1a1a2e !important;
        -webkit-text-fill-color: #1a1a2e !important;
    }
    textarea:focus, [data-testid="stTextArea"] textarea:focus {
        border-color: #4fc3f7 !important;
        box-shadow: 0 0 0 3px rgba(79,195,247,0.15) !important;
        outline: none !important;
    }
    textarea::placeholder, [data-testid="stTextArea"] textarea::placeholder {
        color: #aab0b8 !important;
        -webkit-text-fill-color: #aab0b8 !important;
    }
    /* Hero içindeki tüm metin beyaz kalmalı */
    .hero, .hero * {
        color: inherit !important;
        -webkit-text-fill-color: inherit !important;
    }
    /* Rapor ve normal içerik alanları koyu */
    .report-container p, .report-container li,
    .report-container h1, .report-container h2, .report-container h3,
    .report-container strong, .report-container span {
        color: #1a1a2e !important;
    }
    /* Streamlit markdown render — hero olmayan alanlarda */
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) h1,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) h2,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) h3,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) p,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) li,
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) strong {
        color: #1a1a2e;
        -webkit-text-fill-color: #1a1a2e;
    }
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) h2 {
        border-bottom: 2px solid #e3f2fd;
        padding-bottom: 4px;
    }
    section[data-testid="stMain"] [data-testid="stMarkdownContainer"]:not(.hero) h3 {
        color: #0f3460 !important;
        -webkit-text-fill-color: #0f3460 !important;
    }
    /* Kod blokları — koyu arka planı kaldır */
    [data-testid="stMarkdownContainer"] pre,
    [data-testid="stMarkdownContainer"] code {
        background-color: #f0f4f8 !important;
        color: #1a1a2e !important;
        -webkit-text-fill-color: #1a1a2e !important;
        border: 1px solid #d0d7de !important;
        border-radius: 6px !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stMarkdownContainer"] pre {
        padding: 1rem !important;
        white-space: pre-wrap !important;
        word-break: break-word !important;
    }
    /* Tüm butonlarda yazı beyaz */
    .stButton > button, .stButton > button *,
    .stButton > button span, .stButton > button p {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }
    /* Dosya yükleme butonu */
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button span,
    [data-testid="stFileUploaderDropzone"] span,
    [data-testid="stFileUploaderDropzone"] small {
        color: #e0e0e0 !important;
        -webkit-text-fill-color: #e0e0e0 !important;
    }
    .stAlert { border-radius: 10px !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    .stDownloadButton > button {
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: 2px solid #e0e0e0 !important;
        background: white !important;
        color: #1a1a2e !important;
        transition: all 0.2s !important;
    }
    .stDownloadButton > button:hover {
        border-color: #4fc3f7 !important;
        color: #0f3460 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── PDF üretici ─────────────────────────────────────────────────────────────
def _find_unicode_fonts() -> tuple[str, str] | tuple[None, None]:
    """Cross-platform Unicode font bul. (regular, bold) döndürür; bulamazsa (None, None)."""
    candidates = [
        # Windows
        (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf"),
        # Ubuntu / Streamlit Cloud
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        # Ubuntu Liberation
        ("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"),
        # macOS
        ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
        ("/System/Library/Fonts/Supplemental/Arial.ttf",
         "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ]
    for regular, bold in candidates:
        if Path(regular).exists() and Path(bold).exists():
            return regular, bold
    return None, None


def _generate_pdf(markdown_text: str) -> bytes:
    regular_font, bold_font = _find_unicode_fonts()
    if not regular_font:
        raise RuntimeError(
            "PDF oluşturmak için gerekli font bulunamadı. "
            "Raporu .txt olarak indirmeyi deneyin."
        )

    pdf = FPDF()
    pdf.set_margins(left=15, top=15, right=15)
    pdf.add_font("Arial", "", regular_font)
    pdf.add_font("Arial", "B", bold_font)

    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    W = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_fill_color(26, 26, 46)
    pdf.rect(0, 0, 210, 32, "F")
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(15, 10)
    pdf.cell(W, 12, "CV Doktoru - Analiz Raporu", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(40, 40, 40)

    for line in markdown_text.splitlines():
        stripped = line.strip()
        pdf.set_x(pdf.l_margin)

        if stripped.startswith("### "):
            pdf.set_font("Arial", "B", 12)
            pdf.set_text_color(15, 52, 96)
            pdf.ln(3)
            pdf.multi_cell(W, 8, stripped[4:])
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(40, 40, 40)
        elif stripped.startswith("## "):
            pdf.set_font("Arial", "B", 13)
            pdf.set_text_color(26, 26, 46)
            pdf.ln(4)
            pdf.multi_cell(W, 9, stripped[3:])
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(40, 40, 40)
        elif stripped.startswith("# "):
            pdf.set_font("Arial", "B", 15)
            pdf.set_text_color(26, 26, 46)
            pdf.ln(5)
            pdf.multi_cell(W, 10, stripped[2:])
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(40, 40, 40)
        elif stripped.startswith("**") and stripped.endswith("**"):
            pdf.set_font("Arial", "B", 11)
            pdf.multi_cell(W, 7, stripped.strip("*"))
            pdf.set_font("Arial", "", 11)
        elif stripped in ("", "---"):
            pdf.ln(3)
        else:
            clean = stripped.replace("**", "").replace("*", "").replace("`", "")
            pdf.multi_cell(W, 7, clean)

    return bytes(pdf.output())


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
    <div class="hero-badge">🇹🇷 Türkiye'ye Özel Yapay Zeka Analizi</div>
    <h1>CV'nizi <span>Doğru İş İçin</span><br>Optimize Edin</h1>
    <p>
        CV oluşturmak değil, <strong style="color:#e0f7fa">hedeflediğiniz pozisyon için doğru mesajı vermek</strong> önemlidir.
        Türk iş kültürünü bilen yapay zeka ile saniyeler içinde analiz edin.
    </p>
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-number">🆓</span>
            <span class="stat-label">Ücretsiz</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">🔒</span>
            <span class="stat-label">Kayıt yok</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">🇹🇷</span>
            <span class="stat-label">Türkiye'ye özel</span>
        </div>
        <div class="stat-item">
            <span class="stat-number">🧠</span>
            <span class="stat-label">Claude 4 destekli</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# NASIL ÇALIŞIR
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="how-it-works">
    <div class="how-title">⚡ 3 ADIMDA SONUÇ</div>
    <div class="steps">
        <div class="step">
            <div class="step-icon">📄</div>
            <div class="step-title">CV'nizi Yükleyin</div>
            <div class="step-desc">PDF veya metin olarak yapıştırın</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-icon">💼</div>
            <div class="step-title">İlanı Girin</div>
            <div class="step-desc">Başvurmak istediğiniz pozisyonun ilanını yapıştırın</div>
        </div>
        <div class="step-arrow">→</div>
        <div class="step">
            <div class="step-icon">📋</div>
            <div class="step-title">Raporunuzu Alın</div>
            <div class="step-desc">Kişisel analiz + somut öneriler</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# FARK KARTI
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="diff-card">
    <div class="diff-card-title">🎯 Neden CV Doktoru farklı?</div>
    <div class="diff-items">
        <div class="diff-item">✅ İş ilanına özel eşleştirme</div>
        <div class="diff-item">✅ Türk iş kültürü nüansları</div>
        <div class="diff-item">✅ Somut düzeltme önerileri</div>
        <div class="diff-item">✅ ATS anahtar kelime analizi</div>
        <div class="diff-item">✅ Ücretsiz & sınırsız</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# GİRİŞ FORMU
# ════════════════════════════════════════════════════════════════════════════
col_cv, col_job = st.columns(2, gap="large")

with col_cv:
    st.markdown("""
    <div class="form-card">
        <div class="form-label">📄 CV'niz</div>
    </div>
    """, unsafe_allow_html=True)

    cv_tab_upload, cv_tab_paste = st.tabs(["📎 PDF Yükle", "✏️ Metin Yapıştır"])

    with cv_tab_upload:
        uploaded_cv = st.file_uploader(
            "CV Dosyası",
            type=["pdf", "docx"],
            label_visibility="collapsed",
            help="PDF veya Word (.docx) formatında yükleyebilirsiniz.",
        )
        if uploaded_cv:
            st.success(f"✅ Yüklendi: **{uploaded_cv.name}**")

    with cv_tab_paste:
        cv_text_input = st.text_area(
            "CV Metni",
            height=280,
            placeholder="CV içeriğinizi buraya yapıştırın...\n\nAd Soyad\nİletişim bilgileri\nDeneyim...",
            label_visibility="collapsed",
        )

with col_job:
    st.markdown("""
    <div class="form-card">
        <div class="form-label">💼 Hedef İş İlanı</div>
    </div>
    """, unsafe_allow_html=True)

    job_text_input = st.text_area(
        "İş İlanı",
        height=350,
        placeholder="Başvurmak istediğiniz iş ilanını buraya yapıştırın...\n\nÖrnek:\nPozisyon: Yazılım Geliştirici\nŞirket: Örnek A.Ş.\n\nGereksinimler:\n- 3+ yıl Python deneyimi\n- ...",
        label_visibility="collapsed",
    )

# ── Analiz butonu ────────────────────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
_, btn_col, _ = st.columns([1.5, 4, 1.5])
with btn_col:
    analyze_clicked = st.button(
        "🔍  Analizi Başlat  —  Ücretsiz",
        use_container_width=True,
    )

# ── Güven rozetleri ──────────────────────────────────────────────────────────
st.markdown("""
<div class="trust-bar">
    <div class="trust-item"><span class="trust-icon">🔒</span> SSL ile Güvenli</div>
    <div class="trust-item"><span class="trust-icon">🗑️</span> Verileriniz saklanmaz</div>
    <div class="trust-item"><span class="trust-icon">⚡</span> Anında sonuç</div>
    <div class="trust-item"><span class="trust-icon">🎓</span> Claude 4 destekli</div>
    <div class="trust-item"><span class="trust-icon">🇹🇷</span> Türkçe optimizasyon</div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# ANALİZ MANTIĞI
# ════════════════════════════════════════════════════════════════════════════
if analyze_clicked:
    cv_text = ""

    if uploaded_cv is not None:
        suffix = Path(uploaded_cv.name).suffix.lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_cv.read())
            tmp_path = tmp.name
        try:
            if suffix == ".pdf":
                cv_text = extract_text_from_pdf(tmp_path)
            elif suffix == ".docx":
                cv_text = extract_text_from_docx(tmp_path)
            else:
                st.error(f"Desteklenmeyen format: {suffix}")
        except Exception as e:
            st.error(f"Dosya okunamadı: {e}")
        finally:
            Path(tmp_path).unlink(missing_ok=True)
    elif cv_text_input.strip():
        cv_text = cv_text_input.strip()

    if not cv_text:
        st.warning("⚠️ Lütfen bir CV yükleyin veya CV metnini yapıştırın.")
        st.stop()

    if not job_text_input.strip():
        st.warning("⚠️ Lütfen iş ilanı metnini girin.")
        st.stop()

    doctor = CVDoctor()

    with st.status("🔍 Analiz başlatılıyor...", expanded=True) as status:
        st.write("📄 CV metni işleniyor ve yapılandırılıyor...")
        time.sleep(0.4)
        st.write("💼 İş ilanı inceleniyor, gereksinimler çıkarılıyor...")
        time.sleep(0.4)
        st.write("🇹🇷 Türk iş kültürü veritabanı yükleniyor...")
        time.sleep(0.4)
        st.write("🧠 Yapay zeka motoru devreye alınıyor...")
        status.update(label="⏳ Rapor yazılıyor...", expanded=False)

    try:
        report = st.write_stream(doctor.analyze_stream(cv_text, job_text_input.strip()))
        st.session_state["report"] = report
        st.rerun()
    except Exception as e:
        st.error(f"Analiz sırasında hata oluştu: {e}")
        st.stop()

# ════════════════════════════════════════════════════════════════════════════
# RAPOR GÖSTERİMİ
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.get("report"):
    report = st.session_state["report"]

    st.markdown("""
    <div class="report-container">
        <div class="report-header">
            <span style="font-size:1.8rem">📋</span>
            <h2>Analiz Raporu</h2>
            <span class="report-badge">YAPAY ZEKA ANALİZİ</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(report)

    st.divider()

    st.markdown("**⬇️ Raporunuzu indirin:**")
    dl_col1, dl_col2, _ = st.columns([2, 2, 3])

    with dl_col1:
        st.download_button(
            label="📄 Metin olarak indir (.txt)",
            data=report.encode("utf-8"),
            file_name="cv_analiz_raporu.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_txt",
        )

    with dl_col2:
        if st.button("📕 PDF olarak indir", use_container_width=True, key="btn_pdf"):
            try:
                pdf_bytes = _generate_pdf(report)
                st.download_button(
                    label="⬇️ PDF'yi kaydet",
                    data=pdf_bytes,
                    file_name="cv_analiz_raporu.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="dl_pdf",
                )
            except RuntimeError as e:
                st.warning(str(e))

    st.markdown("""
    <br>
    <div style="text-align:center; color:#78909c; font-size:0.85rem; padding: 1rem 0 2rem 0;">
        CV Doktoru — Türkiye'nin iş ilanına özel CV analiz aracı
    </div>
    """, unsafe_allow_html=True)
