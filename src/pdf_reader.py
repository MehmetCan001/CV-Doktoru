"""
PDF'den metin çıkarma.
Basit ama yeterli - pypdf kullanır.
"""

from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(pdf_path: str | Path) -> str:
    """
    PDF dosyasından düz metin çıkar.

    Args:
        pdf_path: PDF dosyasının yolu

    Returns:
        Birleşik metin (tüm sayfaların metni)
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"PDF bulunamadı: {path}")

    if not path.suffix.lower() == ".pdf":
        raise ValueError(f"PDF değil: {path.name}")

    reader = PdfReader(str(path))
    pages = []

    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages.append(text)

    return "\n\n".join(pages)


def extract_text_smart(input_data: str | Path) -> str:
    """
    Akıllı metin çıkarıcı:
    - Eğer PDF dosya yolu ise → PDF'den çıkar
    - Eğer .txt dosya yolu ise → direkt oku
    - Eğer düz metin ise → öyle döndür
    """
    # Eğer string ve dosya gibi görünmüyorsa, düz metindir
    input_str = str(input_data)

    if len(input_str) > 500 or "\n" in input_str:
        # Muhtemelen yapıştırılmış metin
        return input_str

    path = Path(input_str)
    if not path.exists():
        # Dosya değilse düz metin kabul et
        return input_str

    if path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(path)

    if path.suffix.lower() in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")

    raise ValueError(f"Desteklenmeyen format: {path.suffix}")
