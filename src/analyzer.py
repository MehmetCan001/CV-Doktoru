"""
CV analiz motorunun kalbi.
Claude API'ye gönderir, raporu alır.
"""

import os
from anthropic import Anthropic

from src import config
from src.prompt_loader import (
    load_system_prompt,
    load_analysis_prompt,
    load_few_shot_examples,
)


class CVDoctor:
    """CV Doktoru — Ana analiz sınıfı."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model or config.CLAUDE_MODEL

        # Prompt'ları başlangıçta yükle (her çağrıda dosyadan okumamak için)
        self.system_prompt = load_system_prompt()
        self.few_shot_examples = load_few_shot_examples()

    def analyze(self, cv_text: str, job_ad: str) -> str:
        """
        Bir CV'yi iş ilanına göre analiz et.

        Args:
            cv_text: PDF'den veya metin olarak verilen CV içeriği
            job_ad: Hedef iş ilanı metni

        Returns:
            Markdown formatında analiz raporu
        """
        user_message = load_analysis_prompt(cv_text, job_ad)

        # Mesaj zincirini kur:
        # 1. Few-shot örnekler (varsa)
        # 2. Asıl kullanıcı sorusu
        messages = list(self.few_shot_examples)
        messages.append({
            "role": "user",
            "content": user_message,
        })

        response = self.client.messages.create(
            model=self.model,
            max_tokens=config.MAX_TOKENS,
            system=self.system_prompt,
            messages=messages,
        )

        # Cevap metnini topla
        return "".join(block.text for block in response.content if hasattr(block, "text"))

    def quick_test(self) -> str:
        """
        Hızlı duman testi (smoke test).
        API çalışıyor mu? Prompt'lar doğru yükleniyor mu?
        """
        response = self.client.messages.create(
            model=self.model,
            max_tokens=200,
            system=self.system_prompt,
            messages=[{
                "role": "user",
                "content": "Kim olduğunu ve ne yaptığını 2 cümleyle anlat."
            }],
        )
        return "".join(block.text for block in response.content if hasattr(block, "text"))
