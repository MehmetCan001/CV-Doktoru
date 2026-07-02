"""
Analiz raporunu PDF'e dönüştürme.
Streamlit'ten bağımsız — hem app.py hem server.py tarafından kullanılabilir.
"""

from pathlib import Path
from fpdf import FPDF


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


def generate_pdf_report(markdown_text: str) -> bytes:
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

    pdf.set_fill_color(15, 23, 42)
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
            pdf.set_text_color(30, 64, 175)
            pdf.ln(3)
            pdf.multi_cell(W, 8, stripped[4:])
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(40, 40, 40)
        elif stripped.startswith("## "):
            pdf.set_font("Arial", "B", 13)
            pdf.set_text_color(15, 23, 42)
            pdf.ln(4)
            pdf.multi_cell(W, 9, stripped[3:])
            pdf.set_font("Arial", "", 11)
            pdf.set_text_color(40, 40, 40)
        elif stripped.startswith("# "):
            pdf.set_font("Arial", "B", 15)
            pdf.set_text_color(15, 23, 42)
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
