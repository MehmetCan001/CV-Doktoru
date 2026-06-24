"""
Konfigürasyon ve yol ayarları.
"""

import os
from pathlib import Path

# Proje kök dizini
PROJECT_ROOT = Path(__file__).parent.parent

# Klasör yolları
PROMPTS_DIR = PROJECT_ROOT / "prompts"
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
EXAMPLES_DIR = PROMPTS_DIR / "examples"
DATA_DIR = PROJECT_ROOT / "data"
TESTS_DIR = PROJECT_ROOT / "tests"

# Anthropic Claude API ayarları
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
MAX_TOKENS = 32768

# Bilgi tabanı kullanılsın mı? (RAG benzeri sistem)
USE_KNOWLEDGE_BASE = True

# Few-shot örnek kullanılsın mı?
USE_FEW_SHOT_EXAMPLES = True
