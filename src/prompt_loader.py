"""
Prompt yönetimi.
Markdown dosyalarından prompt'ları okur, bağlamı zenginleştirir.

Bu modül prompt mühendisliğinin kalbidir:
- system_prompt.md: Claude'un kimliği
- analysis_prompt.md: Çıktı formatı
- knowledge/*.md: Türk iş kültürü bilgi tabanı
- examples/*.md: Few-shot örnekler
"""

from pathlib import Path
from src import config


def read_file(path: Path) -> str:
    """Bir dosyayı oku, içeriğini döndür."""
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def load_system_prompt() -> str:
    """
    Sistem prompt'unu yükle ve bilgi tabanını ekle.
    Claude'un her API çağrısında 'kim olduğunu' tanımlar.
    """
    parts = []

    # Ana kimlik
    system = read_file(config.PROMPTS_DIR / "system_prompt.md")
    parts.append(system)

    # Bilgi tabanını ekle
    if config.USE_KNOWLEDGE_BASE:
        parts.append("\n\n---\n\n# DERINLIKLI BİLGİ TABANI\n")
        parts.append("Aşağıda Türk iş kültürü hakkında detaylı bilgi var. "
                     "Analiz yaparken bu bilgileri kullan.\n\n")

        for kb_file in sorted(config.KNOWLEDGE_DIR.glob("*.md")):
            parts.append(f"## {kb_file.stem.replace('_', ' ').title()}\n\n")
            parts.append(read_file(kb_file))
            parts.append("\n\n")

    return "".join(parts)


def load_analysis_prompt(cv_text: str, job_ad: str) -> str:
    """
    Analiz prompt'unu yükle ve placeholder'ları doldur.

    Args:
        cv_text: PDF'den çıkarılmış CV metni
        job_ad: Kullanıcının yapıştırdığı iş ilanı

    Returns:
        Doldurulmuş, gönderilmeye hazır prompt
    """
    template = read_file(config.PROMPTS_DIR / "analysis_prompt.md")

    # Placeholder'ları doldur
    return template.format(cv_text=cv_text, job_ad=job_ad)


def load_few_shot_examples() -> list[dict]:
    """
    Few-shot örnekleri yükle.
    Bu örnekler Claude'a "doğru çıktı nasıl görünür" gösterir.

    Returns:
        Anthropic mesaj formatında örnek liste:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    """
    if not config.USE_FEW_SHOT_EXAMPLES:
        return []

    examples = []

    for example_file in sorted(config.EXAMPLES_DIR.glob("ornek_*.md")):
        content = read_file(example_file)

        # Örnekleri "GİRDİ" ve "DOĞRU ÇIKTI" olarak böl
        if "## DOĞRU ÇIKTI" in content:
            input_part, output_part = content.split("## DOĞRU ÇIKTI", 1)

            examples.append({
                "role": "user",
                "content": input_part.strip(),
            })
            examples.append({
                "role": "assistant",
                "content": output_part.strip(),
            })

    return examples


def get_full_context_size() -> dict:
    """Yüklenen prompt'ların boyutunu raporla (debug için)."""
    system = load_system_prompt()
    examples = load_few_shot_examples()

    example_chars = sum(len(e["content"]) for e in examples)

    return {
        "system_prompt_chars": len(system),
        "system_prompt_tokens_estimate": len(system) // 3,  # Kabaca
        "examples_count": len(examples) // 2,
        "examples_chars": example_chars,
        "examples_tokens_estimate": example_chars // 3,
        "total_tokens_estimate": (len(system) + example_chars) // 3,
    }
