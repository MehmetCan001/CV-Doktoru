"""Anthropic Claude implementasyonu."""

import os
import threading
import anthropic

from src import config
from src.prompt_loader import load_system_prompt, load_analysis_prompt, load_few_shot_examples


_TIMEOUT = 600  # saniye — büyük Türkçe promptlar 2-4 dk sürebilir

class CVDoctor:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model_name = model or config.CLAUDE_MODEL
        self.system_prompt = load_system_prompt()
        self.few_shot_examples = load_few_shot_examples()

    def _build_client(self) -> anthropic.Anthropic:
        """Her çağrı için izole client — Streamlit event loop çakışmasını önler."""
        return anthropic.Anthropic(api_key=self.api_key, timeout=_TIMEOUT)

    def analyze(self, cv_text: str, job_ad: str) -> str:
        """Blocking analiz — ayrı thread'de çalışır, event loop çakışmasını önler."""
        user_message = load_analysis_prompt(cv_text, job_ad)
        messages = [*self.few_shot_examples, {"role": "user", "content": user_message}]
        model_name = self.model_name
        system_prompt = self.system_prompt
        api_key = self.api_key

        result: list = [None]
        error: list = [None]
        done = threading.Event()

        def _call():
            try:
                client = anthropic.Anthropic(api_key=api_key, timeout=_TIMEOUT)
                result[0] = client.messages.create(
                    model=model_name,
                    max_tokens=config.MAX_TOKENS,
                    system=system_prompt,
                    messages=messages,
                    temperature=0,
                )
            except Exception as exc:
                error[0] = exc
            finally:
                done.set()

        t = threading.Thread(target=_call, daemon=True)
        t.start()
        if not done.wait(timeout=_TIMEOUT):
            raise TimeoutError(f"API yanıt vermedi ({_TIMEOUT}s).")
        if error[0] is not None:
            raise error[0]
        response = result[0]

        text = response.content[0].text
        if response.stop_reason == "max_tokens":
            text += "\n\n---\n\n> ⚠️ **Rapor token limitine ulaştığı için kesildi.** CV veya iş ilanı metnini kısaltmayı deneyin."
        return text

    def analyze_stream(self, cv_text: str, job_ad: str):
        """Text chunk'larını yield eden streaming analiz."""
        user_message = load_analysis_prompt(cv_text, job_ad)
        messages = [*self.few_shot_examples, {"role": "user", "content": user_message}]
        with self.client.messages.stream(
            model=self.model_name,
            max_tokens=config.MAX_TOKENS,
            system=self.system_prompt,
            messages=messages,
            temperature=0,
        ) as stream:
            for text in stream.text_stream:
                yield text
            if stream.get_final_message().stop_reason == "max_tokens":
                yield "\n\n---\n\n> ⚠️ **Rapor token limitine ulaştığı için kesildi.** CV veya iş ilanı metnini kısaltmayı deneyin."

    def quick_test(self) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=200,
            system=self.system_prompt,
            messages=[{"role": "user", "content": "Kim olduğunu ve ne yaptığını 2 cümleyle anlat."}],
        )
        return response.content[0].text
