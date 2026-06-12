"""Google Gemini implementasyonu — geçici, ANTHROPIC_API_KEY yokken kullanılır."""

import os
from google import genai
from google.genai import types

from src import config
from src.prompt_loader import load_system_prompt, load_analysis_prompt, load_few_shot_examples


class CVDoctor:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.client = genai.Client(api_key=api_key or os.getenv("GEMINI_API_KEY"))
        self.model_name = model or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.system_prompt = load_system_prompt()
        self.few_shot_examples = load_few_shot_examples()

    def analyze(self, cv_text: str, job_ad: str) -> str:
        import time
        from google.genai.errors import ServerError

        user_message = load_analysis_prompt(cv_text, job_ad)

        history = []
        for msg in self.few_shot_examples:
            history.append(
                types.Content(
                    role="user" if msg["role"] == "user" else "model",
                    parts=[types.Part(text=msg["content"])],
                )
            )

        gemini_config = types.GenerateContentConfig(
            system_instruction=self.system_prompt,
            max_output_tokens=config.MAX_TOKENS,
            temperature=0,
            # Gemini 2.5'in dahili "thinking" süreci temperature=0'ı etkisiz kılar.
            # Skor tutarlılığı için thinking'i devre dışı bırakıyoruz.
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        for attempt in range(3):
            try:
                chat = self.client.chats.create(
                    model=self.model_name,
                    config=gemini_config,
                    history=history,
                )
                return chat.send_message(user_message).text
            except ServerError as e:
                if e.status_code == 503 and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                raise RuntimeError(
                    "Yapay zeka servisi şu an yoğun. Lütfen birkaç saniye bekleyip tekrar deneyin."
                ) from e

    def quick_test(self) -> str:
        response = self.client.models.generate_content(
            model=self.model_name,
            contents="Kim olduğunu ve ne yaptığını 2 cümleyle anlat.",
            config=types.GenerateContentConfig(
                system_instruction=self.system_prompt,
                max_output_tokens=200,
            ),
        )
        return response.text
