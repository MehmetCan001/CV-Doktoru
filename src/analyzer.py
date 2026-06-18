"""
CV analiz motoru.
ANTHROPIC_API_KEY varsa Claude, yoksa Gemini kullanır.
15 Haziran'da ANTHROPIC_API_KEY eklenince otomatik Claude'a geçer.
"""

import os


def _build_doctor():
    """API key'e göre doğru CVDoctor implementasyonunu döndür."""
    if os.getenv("ANTHROPIC_API_KEY"):
        from src._analyzer_claude import CVDoctor
    else:
        from src._analyzer_gemini import CVDoctor
    return CVDoctor


class CVDoctor:
    """CV Doktoru — API key'e göre Claude veya Gemini kullanır."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        impl_class = _build_doctor()
        self._impl = impl_class(api_key=api_key, model=model)

    def analyze(self, cv_text: str, job_ad: str) -> str:
        return self._impl.analyze(cv_text, job_ad)

    def analyze_stream(self, cv_text: str, job_ad: str):
        """Streaming destekleniyorsa chunk'ları yield eder, yoksa tek parça döner."""
        if hasattr(self._impl, "analyze_stream"):
            yield from self._impl.analyze_stream(cv_text, job_ad)
        else:
            yield self._impl.analyze(cv_text, job_ad)

    def quick_test(self) -> str:
        return self._impl.quick_test()
