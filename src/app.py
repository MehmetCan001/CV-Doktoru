"""
CV Doktoru — Streamlit Web Arayüzü

Başlatmak için:
    streamlit run src/app.py
"""

import os
import re
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
from dotenv import load_dotenv

from src.analyzer import CVDoctor
from src.pdf_reader import extract_text_from_pdf, extract_text_from_docx
from src.rate_limiter import check_and_increment, get_client_ip, remaining_today, DAILY_LIMIT
from src.pdf_export import generate_pdf_report

load_dotenv()

def _round_score(report: str) -> str:
    """Rapordaki X/100 skorunu en yakın 5'e yuvarlar (LLM varyansını gizler)."""
    def _replace(m):
        rounded = round(int(m.group(1)) / 5) * 5
        return f"**{rounded}/100**"
    return re.sub(r"\*\*(\d+)/100\*\*", _replace, report)


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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }

[data-testid="stAppViewContainer"] {
    background: #F1F5F9;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
[data-testid="stHeader"] { background: transparent; }
.block-container {
    padding-top: 0 !important;
    max-width: 1100px;
    padding-left: 1.5rem !important;
    padding-right: 1.5rem !important;
}

/* ── Hero ── */
.hero-wrapper {
    background: linear-gradient(160deg, #0F172A 0%, #1E293B 55%, #0F172A 100%);
    padding: 4rem 2rem 3.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-wrapper::before {
    content: '';
    position: absolute;
    inset: 0;
    background-image: radial-gradient(circle, rgba(56,189,248,0.07) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
}
.hero-wrapper::after {
    content: '';
    position: absolute;
    top: -40%;
    left: 50%;
    transform: translateX(-50%);
    width: 700px;
    height: 500px;
    background: radial-gradient(ellipse, rgba(56,189,248,0.1) 0%, transparent 65%);
    pointer-events: none;
}
.hero-inner {
    position: relative;
    z-index: 1;
    text-align: center;
    max-width: 700px;
    margin: 0 auto;
}
.hero-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(56,189,248,0.08);
    border: 1px solid rgba(56,189,248,0.22);
    color: #7DD3FC !important;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 0.4rem 1.1rem;
    border-radius: 100px;
    margin-bottom: 1.5rem;
}
.hero-title {
    font-size: 3rem;
    font-weight: 900;
    color: #F8FAFC !important;
    line-height: 1.1;
    margin-bottom: 1.25rem;
    letter-spacing: -0.03em;
}
.hero-title .accent { color: #38BDF8 !important; }
.hero-subtitle {
    font-size: 1.05rem;
    color: #94A3B8 !important;
    max-width: 520px;
    margin: 0 auto 2.5rem;
    line-height: 1.8;
}
.hero-stats {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    flex-wrap: wrap;
}
.hero-stat-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    padding: 0.4rem 0.9rem;
    border-radius: 100px;
    font-size: 0.8rem;
    font-weight: 600;
    color: #CBD5E1 !important;
    transition: all 0.2s;
}

/* ── Section cards ── */
.section-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 2rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 20px rgba(0,0,0,0.05);
    border: 1px solid #E2E8F0;
    margin-bottom: 1.5rem;
}
.section-label {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 1.75rem;
    text-align: center;
}

/* ── Steps ── */
.steps-grid {
    display: flex;
    align-items: flex-start;
    justify-content: center;
}
.step-item {
    flex: 1;
    max-width: 210px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 0 0.75rem;
}
.step-icon-box {
    width: 56px;
    height: 56px;
    background: linear-gradient(135deg, #0F172A, #1E3A5F);
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    margin-bottom: 0.85rem;
    box-shadow: 0 4px 16px rgba(15,23,42,0.18);
}
.step-connector {
    flex: 0 0 36px;
    height: 2px;
    background: linear-gradient(90deg, #CBD5E1, #38BDF8, #CBD5E1);
    margin-top: 28px;
    border-radius: 2px;
}
.step-name {
    font-size: 0.88rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.25rem;
}
.step-desc-text { font-size: 0.77rem; color: #94A3B8; line-height: 1.5; }

/* ── Why card ── */
.why-card {
    background: #F0FDF4;
    border: 1.5px solid #86EFAC;
    border-radius: 14px;
    padding: 1.25rem 1.75rem;
    margin-bottom: 1.5rem;
}
.why-card-title {
    font-size: 0.82rem;
    font-weight: 800;
    color: #15803D;
    letter-spacing: 0.3px;
    margin-bottom: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.why-items { display: flex; gap: 0.6rem; flex-wrap: wrap; }
.why-item {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    font-size: 0.83rem;
    font-weight: 600;
    color: #16A34A;
    background: rgba(22,163,74,0.08);
    padding: 0.3rem 0.75rem 0.3rem 0.45rem;
    border-radius: 8px;
    border: 1px solid rgba(22,163,74,0.15);
}
.why-check {
    width: 17px;
    height: 17px;
    background: #16A34A;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 0.6rem;
    color: white;
    flex-shrink: 0;
    font-weight: 900;
}

/* ── Form labels ── */
.form-section-label {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    font-size: 0.92rem;
    font-weight: 700;
    color: #0F172A;
    margin-bottom: 0.75rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #F1F5F9;
}
.form-label-icon {
    width: 32px;
    height: 32px;
    background: #F1F5F9;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
    flex-shrink: 0;
}

/* ── Inputs ── */
textarea, input,
[data-testid="stTextArea"] textarea,
.stTextArea textarea,
div[data-baseweb="textarea"] textarea {
    border-radius: 10px !important;
    border: 1.5px solid #E2E8F0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.89rem !important;
    background-color: #FAFAFA !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
textarea:focus, [data-testid="stTextArea"] textarea:focus {
    border-color: #38BDF8 !important;
    box-shadow: 0 0 0 3px rgba(56,189,248,0.12) !important;
    background-color: #FFFFFF !important;
    outline: none !important;
}
textarea::placeholder {
    color: #94A3B8 !important;
    -webkit-text-fill-color: #94A3B8 !important;
}

/* ── CTA Button ── */
.stButton > button {
    background: linear-gradient(135deg, #0EA5E9 0%, #2563EB 100%) !important;
    color: white !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    padding: 0.9rem 2rem !important;
    border-radius: 12px !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(14,165,233,0.38) !important;
    transition: all 0.25s ease !important;
    letter-spacing: 0.1px !important;
}
.stButton > button:hover {
    box-shadow: 0 8px 24px rgba(14,165,233,0.52), 0 0 0 4px rgba(56,189,248,0.15) !important;
    transform: translateY(-2px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }
.stButton > button, .stButton > button *,
.stButton > button span, .stButton > button p {
    color: white !important;
    -webkit-text-fill-color: white !important;
}

/* ── Trust bar ── */
.trust-bar {
    display: flex;
    justify-content: center;
    gap: 2rem;
    flex-wrap: wrap;
    padding: 1.25rem 0 0.25rem;
}
.trust-item {
    display: flex;
    align-items: center;
    gap: 0.4rem;
    font-size: 0.79rem;
    color: #94A3B8;
    font-weight: 500;
}

/* ── Report header ── */
.report-header-card {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border-radius: 16px 16px 0 0;
    padding: 1.6rem 2rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.report-icon-box {
    width: 46px;
    height: 46px;
    background: rgba(56,189,248,0.12);
    border: 1px solid rgba(56,189,248,0.2);
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.4rem;
    flex-shrink: 0;
}
.report-header-info { flex: 1; }
.report-header-info h2 {
    font-size: 1.15rem !important;
    font-weight: 800 !important;
    color: #F8FAFC !important;
    -webkit-text-fill-color: #F8FAFC !important;
    margin: 0 0 0.15rem !important;
    line-height: 1.3 !important;
}
.report-header-info p {
    font-size: 0.78rem !important;
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
    margin: 0 !important;
}
.report-ai-badge {
    background: rgba(56,189,248,0.12);
    border: 1px solid rgba(56,189,248,0.22);
    color: #38BDF8;
    font-size: 0.65rem;
    font-weight: 700;
    padding: 0.3rem 0.65rem;
    border-radius: 6px;
    letter-spacing: 1.2px;
    white-space: nowrap;
}

/* ── Markdown rendering (report body) ── */
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] h1,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] h2,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] h3,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] li,
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] strong {
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    font-family: 'Inter', sans-serif !important;
}
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] h2 {
    font-size: 1rem !important;
    font-weight: 800 !important;
    border-bottom: 2px solid #F1F5F9 !important;
    padding-bottom: 5px !important;
    margin-top: 1.75rem !important;
    letter-spacing: 0.2px !important;
}
section[data-testid="stMain"] [data-testid="stMarkdownContainer"] h3 {
    color: #1E40AF !important;
    -webkit-text-fill-color: #1E40AF !important;
    font-size: 0.93rem !important;
    font-weight: 700 !important;
}
[data-testid="stMarkdownContainer"] pre,
[data-testid="stMarkdownContainer"] code {
    background-color: #F8FAFC !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
    font-size: 0.86rem !important;
}
[data-testid="stMarkdownContainer"] pre {
    padding: 1rem !important;
    white-space: pre-wrap !important;
    word-break: break-word !important;
}

/* ── Download & misc ── */
.stDownloadButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    border: 1.5px solid #E2E8F0 !important;
    background: white !important;
    color: #0F172A !important;
    -webkit-text-fill-color: #0F172A !important;
    transition: all 0.2s !important;
    font-family: 'Inter', sans-serif !important;
}
.stDownloadButton > button:hover {
    border-color: #38BDF8 !important;
    box-shadow: 0 2px 10px rgba(14,165,233,0.15) !important;
}
[data-testid="stFileUploader"] button,
[data-testid="stFileUploader"] button span,
[data-testid="stFileUploaderDropzone"] span,
[data-testid="stFileUploaderDropzone"] small {
    color: #64748B !important;
    -webkit-text-fill-color: #64748B !important;
}
.stAlert { border-radius: 12px !important; }
.stTabs [data-baseweb="tab-list"] { gap: 0.5rem; }
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* ── Loading animasyonu ── */
.cv-loading-card {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border-radius: 16px;
    padding: 2.5rem 2rem;
    text-align: center;
    margin: 1.5rem 0;
    border: 1px solid rgba(56,189,248,0.18);
    box-shadow: 0 8px 32px rgba(0,0,0,0.18);
}
.cv-loading-icon {
    font-size: 2.4rem;
    display: block;
    animation: cv-pulse 1.6s ease-in-out infinite;
}
@keyframes cv-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.12); }
}
.cv-loading-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #F8FAFC;
    margin: 0.9rem 0 0.5rem;
    font-family: 'Inter', sans-serif;
}
.cv-loading-dots { margin-bottom: 0.25rem; }
.cv-loading-dots span {
    display: inline-block;
    width: 6px; height: 6px;
    background: #38BDF8;
    border-radius: 50%;
    margin: 0 3px;
    animation: cv-dot 1.4s ease-in-out infinite;
}
.cv-loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.cv-loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes cv-dot {
    0%, 80%, 100% { transform: scale(0.55); opacity: 0.35; }
    40% { transform: scale(1); opacity: 1; }
}
.cv-loading-steps {
    position: relative;
    height: 1.8rem;
    margin: 1.25rem 0;
}
.cv-step {
    font-size: 0.84rem;
    font-family: 'Inter', sans-serif;
    position: absolute;
    width: 100%;
    left: 0;
    opacity: 0;
}
@keyframes cv-s1 {
    0%  { opacity:0; color:#94A3B8; }
    2%  { opacity:1; color:#7DD3FC; }
    14% { opacity:1; color:#7DD3FC; }
    17% { opacity:0; }
    100%{ opacity:0; }
}
@keyframes cv-s2 {
    0%,16%{ opacity:0; }
    18%  { opacity:1; color:#7DD3FC; }
    30%  { opacity:1; color:#7DD3FC; }
    33%  { opacity:0; }
    100% { opacity:0; }
}
@keyframes cv-s3 {
    0%,32%{ opacity:0; }
    34%  { opacity:1; color:#7DD3FC; }
    50%  { opacity:1; color:#7DD3FC; }
    53%  { opacity:0; }
    100% { opacity:0; }
}
@keyframes cv-s4 {
    0%,52%{ opacity:0; }
    54%  { opacity:1; color:#7DD3FC; }
    70%  { opacity:1; color:#7DD3FC; }
    73%  { opacity:0; }
    100% { opacity:0; }
}
@keyframes cv-s5 {
    0%,72%{ opacity:0; }
    74%  { opacity:1; color:#7DD3FC; }
    100% { opacity:1; color:#7DD3FC; }
}
.cv-step-1 { animation: cv-s1 150s linear 1 forwards; }
.cv-step-2 { animation: cv-s2 150s linear 1 forwards; }
.cv-step-3 { animation: cv-s3 150s linear 1 forwards; }
.cv-step-4 { animation: cv-s4 150s linear 1 forwards; }
.cv-step-5 { animation: cv-s5 150s linear 1 forwards; }
.cv-loading-bar-wrap {
    background: rgba(255,255,255,0.07);
    border-radius: 100px;
    height: 4px;
    overflow: hidden;
    margin: 1.25rem 0 0.85rem;
}
.cv-loading-bar {
    height: 100%;
    background: linear-gradient(90deg, #0EA5E9, #38BDF8);
    border-radius: 100px;
    animation: cv-progress 150s cubic-bezier(0.15,0.5,0.5,1) 1 forwards;
}
@keyframes cv-progress {
    from { width: 3%; }
    to   { width: 93%; }
}
.cv-loading-note {
    font-size: 0.74rem;
    color: #475569;
    font-family: 'Inter', sans-serif;
}
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-wrapper">
  <div class="hero-inner">
    <div class="hero-badge">🇹🇷 &nbsp;Türkiye'ye Özel Yapay Zeka Analizi</div>
    <div class="hero-title">
      CV'nizi <span class="accent">Doğru İş İçin</span><br>Optimize Edin
    </div>
    <div class="hero-subtitle">
      CV oluşturmak değil, <span style="color:#FFFFFF;-webkit-text-fill-color:#FFFFFF;font-weight:700">hedeflediğiniz pozisyon için doğru mesajı</span> vermeniz önemlidir. Türk iş kültürünü bilen yapay zeka ile analiz edin.
    </div>
    <div class="hero-stats">
      <span class="hero-stat-pill">🆓&nbsp; Ücretsiz</span>
      <span class="hero-stat-pill">🔒&nbsp; Kayıt yok</span>
      <span class="hero-stat-pill">🇹🇷&nbsp; Türkiye'ye özel</span>
      <span class="hero-stat-pill">🧠&nbsp; Claude 4 destekli</span>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# NASIL ÇALIŞIR
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="section-card">
  <div class="section-label">⚡ 3 Adımda Sonuç</div>
  <div class="steps-grid">
    <div class="step-item">
      <div class="step-icon-box">📄</div>
      <div class="step-name">CV'nizi Yükleyin</div>
      <div class="step-desc-text">PDF veya metin olarak yapıştırın</div>
    </div>
    <div class="step-connector"></div>
    <div class="step-item">
      <div class="step-icon-box">💼</div>
      <div class="step-name">İlanı Girin</div>
      <div class="step-desc-text">Başvurmak istediğiniz pozisyonun ilanını yapıştırın</div>
    </div>
    <div class="step-connector"></div>
    <div class="step-item">
      <div class="step-icon-box">📋</div>
      <div class="step-name">Raporunuzu Alın</div>
      <div class="step-desc-text">Kişisel analiz + somut öneriler</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# FARK KARTI
# ════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="why-card">
  <div class="why-card-title">🎯 Neden CV Doktoru Farklı?</div>
  <div class="why-items">
    <span class="why-item"><span class="why-check">✓</span>İş ilanına özel eşleştirme</span>
    <span class="why-item"><span class="why-check">✓</span>Türk iş kültürü nüansları</span>
    <span class="why-item"><span class="why-check">✓</span>Somut düzeltme önerileri</span>
    <span class="why-item"><span class="why-check">✓</span>ATS anahtar kelime analizi</span>
    <span class="why-item"><span class="why-check">✓</span>Ücretsiz &amp; sınırsız</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# GİRİŞ FORMU
# ════════════════════════════════════════════════════════════════════════════
col_cv, col_job = st.columns(2, gap="large")

with col_cv:
    st.markdown("""
    <div class="form-section-label">
      <span class="form-label-icon">📄</span> CV'niz
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
    <div class="form-section-label">
      <span class="form-label-icon">💼</span> Hedef İş İlanı
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

# ── Kalan hak göstergesi ─────────────────────────────────────────────────────
_ip_now = get_client_ip()
_remaining_now = remaining_today(_ip_now)
if _remaining_now < DAILY_LIMIT:
    st.markdown(
        f"<div style='text-align:center;color:#94A3B8;font-size:0.78rem;"
        f"font-family:Inter,sans-serif;margin-top:0.5rem'>"
        f"Bugün {_remaining_now} ücretsiz analiz hakkınız kaldı.</div>",
        unsafe_allow_html=True,
    )

# ── Güven rozetleri ──────────────────────────────────────────────────────────
st.markdown("""
<div class="trust-bar">
  <div class="trust-item">🔒 SSL ile Güvenli</div>
  <div class="trust-item">🗑️ Verileriniz saklanmaz</div>
  <div class="trust-item">⚡ Anında sonuç</div>
  <div class="trust-item">🎓 Claude 4 destekli</div>
  <div class="trust-item">🇹🇷 Türkçe optimizasyon</div>
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

    # Rate limit kontrolü
    _client_ip = get_client_ip()
    _allowed, _remaining = check_and_increment(_client_ip)
    if not _allowed:
        st.error(
            "⏳ **Bugünkü ücretsiz analiz hakkınızı kullandınız** "
            f"(günlük {DAILY_LIMIT} analiz). "
            "Yarın gece yarısı UTC'de yenilenir."
        )
        st.stop()

    # API key kontrolü — yoksa fail-fast
    _api_key_ok = bool(os.getenv("ANTHROPIC_API_KEY") or os.getenv("GEMINI_API_KEY"))
    if not _api_key_ok:
        st.error(
            "⚠️ **API anahtarı bulunamadı.** "
            "Streamlit Cloud → App settings → Secrets bölümüne "
            "`ANTHROPIC_API_KEY` ekleyin ve uygulamayı yeniden başlatın."
        )
        st.stop()

    doctor = CVDoctor()
    report = None

    _loading_slot = st.empty()
    _loading_slot.markdown("""
<div class="cv-loading-card">
  <span class="cv-loading-icon">🩺</span>
  <div class="cv-loading-title">Analiz yapılıyor</div>
  <div class="cv-loading-dots"><span></span><span></span><span></span></div>
  <div class="cv-loading-steps">
    <div class="cv-step cv-step-1">📄 CV metni okunuyor ve ayrıştırılıyor</div>
    <div class="cv-step cv-step-2">🔍 İş ilanıyla eşleştiriliyor</div>
    <div class="cv-step cv-step-3">⚠️ Kırmızı bayraklar tespit ediliyor</div>
    <div class="cv-step cv-step-4">💡 Güçlü noktalar ve öneriler hazırlanıyor</div>
    <div class="cv-step cv-step-5">✍️ Rapor yazılıyor ve düzenleniyor</div>
  </div>
  <div class="cv-loading-bar-wrap"><div class="cv-loading-bar"></div></div>
  <div class="cv-loading-note">Bu işlem 2-3 dakika sürebilir — lütfen sayfayı kapatmayın.</div>
</div>
""", unsafe_allow_html=True)

    import time as _time
    _t0 = _time.time()
    print("CV Doktoru: analiz başladı", flush=True)
    try:
        report = _round_score(doctor.analyze(cv_text, job_text_input.strip()))
        _elapsed = round(_time.time() - _t0)
        print(f"CV Doktoru: analiz tamamlandı — {_elapsed}s, {len(report)} karakter", flush=True)
        _loading_slot.success("✅ Rapor hazır!")
    except Exception as e:
        print(f"CV Doktoru: analiz HATASI — {type(e).__name__}: {e}", flush=True)
        _loading_slot.error(f"**Analiz hatası ({type(e).__name__}):** {e}")
        with st.expander("Teknik detaylar"):
            st.exception(e)
        st.stop()

    # WebSocket kopsa bile raporu kurtarmak için dosyaya yaz
    try:
        _report_file = Path(__file__).parent.parent / "data" / "last_report.txt"
        _report_file.parent.mkdir(exist_ok=True)
        _report_file.write_text(report, encoding="utf-8")
    except Exception:
        pass

    st.session_state["report"] = report

# ════════════════════════════════════════════════════════════════════════════
# RAPOR GÖSTERİMİ
# ════════════════════════════════════════════════════════════════════════════
# session_state yoksa son 30 dk içindeki dosyadan kurtar
_report_to_show = st.session_state.get("report")
if not _report_to_show:
    try:
        import time as _time
        _report_file = Path(__file__).parent.parent / "data" / "last_report.txt"
        if _report_file.exists() and (_time.time() - _report_file.stat().st_mtime) < 1800:
            _report_to_show = _report_file.read_text(encoding="utf-8")
            print("CV Doktoru: rapor dosyadan kurtarıldı", flush=True)
    except Exception:
        pass

if _report_to_show:
    report = _report_to_show

    st.markdown("""
    <div class="report-header-card">
      <div class="report-icon-box">📋</div>
      <div class="report-header-info">
        <h2>Analiz Raporu</h2>
        <p>İş ilanına özel kişisel değerlendirme</p>
      </div>
      <span class="report-ai-badge">YAPAY ZEKA ANALİZİ</span>
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
                pdf_bytes = generate_pdf_report(report)
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
    <div style="text-align:center; color:#94A3B8; font-size:0.82rem; padding: 1rem 0 2rem 0;
                font-family:'Inter',sans-serif;">
        CV Doktoru — Türkiye'nin iş ilanına özel CV analiz aracı
    </div>
    """, unsafe_allow_html=True)
