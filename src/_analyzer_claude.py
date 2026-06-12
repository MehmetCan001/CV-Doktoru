"""Anthropic Claude implementasyonu."""

import os
import anthropic

from src import config
from src.prompt_loader import load_system_prompt, load_analysis_prompt, load_few_shot_examples


class CVDoctor:
    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model_name = model or config.CLAUDE_MODEL
        self.system_prompt = load_system_prompt()
        self.few_shot_examples = load_few_shot_examples()

    def analyze(self, cv_text: str, job_ad: str) -> str:
        user_message = load_analysis_prompt(cv_text, job_ad)
        messages = [*self.few_shot_examples, {"role": "user", "content": user_message}]
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=config.MAX_TOKENS,
            system=self.system_prompt,
            messages=messages,
            temperature=0,
        )
        return response.content[0].text

    def quick_test(self) -> str:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=200,
            system=self.system_prompt,
            messages=[{"role": "user", "content": "Kim olduğunu ve ne yaptığını 2 cümleyle anlat."}],
        )
        return response.content[0].text
