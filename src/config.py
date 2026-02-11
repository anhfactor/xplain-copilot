"""Configuration management for xplain CLI."""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Literal

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supported languages
SupportedLang = Literal["en", "vi", "zh", "ja", "ko", "es", "fr", "de", "pt", "ru"]

LANGUAGE_NAMES: dict[str, str] = {
    "en": "English",
    "vi": "Tiếng Việt",
    "zh": "中文",
    "ja": "日本語",
    "ko": "한국어",
    "es": "Español",
    "fr": "Français",
    "de": "Deutsch",
    "pt": "Português",
    "ru": "Русский",
}

DEFAULT_LANGUAGE: SupportedLang = "en"

# Available AI models on GitHub Models API
DEFAULT_MODEL = "openai/gpt-4o-mini"

AVAILABLE_MODELS: dict[str, str] = {
    "openai/gpt-4o-mini": "Fast & affordable (default)",
    "openai/gpt-4o": "Most capable GPT-4o",
    "openai/gpt-4.1": "Latest GPT-4.1",
    "openai/gpt-4.1-mini": "GPT-4.1 mini — fast",
    "openai/gpt-4.1-nano": "GPT-4.1 nano — fastest",
    "openai/o4-mini": "Reasoning model (o4-mini)",
    "meta/llama-4-scout-17b-16e-instruct": "Llama 4 Scout 17B",
    "meta/llama-4-maverick-17b-128e-instruct-fp8": "Llama 4 Maverick 17B",
    "mistralai/mistral-small-2503": "Mistral Small",
    "deepseek/DeepSeek-R1": "DeepSeek R1 (reasoning)",
    "cohere/cohere-command-a": "Cohere Command A",
}


@dataclass
class Config:
    """Application configuration."""
    
    language: SupportedLang = field(default_factory=lambda: os.getenv("XPLAIN_LANG", DEFAULT_LANGUAGE))
    verbose: bool = field(default_factory=lambda: os.getenv("XPLAIN_VERBOSE", "false").lower() == "true")
    model: str = field(default_factory=lambda: os.getenv("XPLAIN_MODEL", DEFAULT_MODEL))
    
    # Paths
    config_dir: Path = field(default_factory=lambda: Path.home() / ".config" / "xplain")
    cache_dir: Path = field(default_factory=lambda: Path.home() / ".cache" / "xplain")
    
    def __post_init__(self):
        """Ensure directories exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    def language_name(self) -> str:
        """Get full language name."""
        return LANGUAGE_NAMES.get(self.language, "English")


# Global config instance
config = Config()


def get_language_prompt(lang: SupportedLang) -> str:
    """Get language instruction for prompts."""
    if lang == "en":
        return "Respond in English."
    return f"Respond in {LANGUAGE_NAMES.get(lang, 'English')} ({lang})."
