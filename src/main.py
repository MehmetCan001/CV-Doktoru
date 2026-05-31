"""
CLI test arayüzü.

Kullanım:
    # Hızlı test (Claude çalışıyor mu?)
    python -m src.main test

    # CV analiz et
    python -m src.main analyze --cv data/cv.pdf --job data/ilan.txt
    python -m src.main analyze --cv tests/test_cv_ornek.txt --job tests/test_ilan_ornek.txt

    # Prompt boyutunu kontrol et (token tahmini)
    python -m src.main info
"""

import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel

from src.analyzer import CVDoctor
from src.pdf_reader import extract_text_smart
from src.prompt_loader import get_full_context_size


console = Console()


def cmd_test():
    """Hızlı duman testi."""
    console.print(Panel.fit("🩺 [bold]CV Doktoru — Hızlı Test[/bold]", border_style="cyan"))

    doctor = CVDoctor()
    console.print("[dim]API'ye basit bir kimlik sorusu gönderiliyor...[/dim]\n")

    response = doctor.quick_test()
    console.print(Panel(response, title="Claude'un Cevabı", border_style="green"))


def cmd_info():
    """Prompt boyutu bilgisi."""
    console.print(Panel.fit("🩺 [bold]CV Doktoru — Prompt Bilgisi[/bold]", border_style="cyan"))

    info = get_full_context_size()
    for key, value in info.items():
        readable_key = key.replace("_", " ").title()
        if isinstance(value, int) and value > 1000:
            console.print(f"  {readable_key}: [yellow]{value:,}[/yellow]")
        else:
            console.print(f"  {readable_key}: [yellow]{value}[/yellow]")


def cmd_analyze(cv_path: str, job_path: str, output: str | None = None):
    """CV analiz et."""
    console.print(Panel.fit("🩺 [bold]CV Doktoru — CV Analizi[/bold]", border_style="cyan"))

    # Girdileri yükle
    console.print(f"[dim]→ CV okunuyor: {cv_path}[/dim]")
    cv_text = extract_text_smart(cv_path)
    console.print(f"  [green]✓[/green] {len(cv_text)} karakter\n")

    console.print(f"[dim]→ İş ilanı okunuyor: {job_path}[/dim]")
    job_text = extract_text_smart(job_path)
    console.print(f"  [green]✓[/green] {len(job_text)} karakter\n")

    # Analiz
    console.print("[dim]→ Claude analiz ediyor (10-30 saniye sürebilir)...[/dim]\n")
    doctor = CVDoctor()
    report = doctor.analyze(cv_text, job_text)

    # Raporu göster
    console.print(Panel(Markdown(report), title="📋 ANALİZ RAPORU", border_style="green"))

    # Kaydet
    if output:
        Path(output).write_text(report, encoding="utf-8")
        console.print(f"\n[green]✓[/green] Rapor kaydedildi: {output}")


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="CV Doktoru CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # test
    subparsers.add_parser("test", help="Hızlı API testi")

    # info
    subparsers.add_parser("info", help="Prompt boyut bilgisi")

    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="CV analiz et")
    analyze_parser.add_argument("--cv", required=True, help="CV dosyası (PDF veya TXT)")
    analyze_parser.add_argument("--job", required=True, help="İş ilanı dosyası (TXT)")
    analyze_parser.add_argument("--output", "-o", help="Rapor çıktı yolu (opsiyonel)")

    args = parser.parse_args()

    if args.command == "test":
        cmd_test()
    elif args.command == "info":
        cmd_info()
    elif args.command == "analyze":
        cmd_analyze(args.cv, args.job, args.output)


if __name__ == "__main__":
    main()
