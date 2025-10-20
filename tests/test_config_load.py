"""Test configuration loading."""
from lyricflow.utils.config import Config

config = Config.load()

print(f"Gemini Model: {config.api.gemini_model}")
print(f"OpenAI Model: {config.api.openai_model}")
print(f"API Provider: {config.api.default_provider}")
