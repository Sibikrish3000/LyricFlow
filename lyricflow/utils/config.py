"""Configuration management for LyricFlow."""

import os
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
from dataclasses import dataclass, field


@dataclass
class APIConfig:
    """API configuration for romanization and translation services."""
    default_provider: str = "local"
    openai_api_key: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"
    gemini_api_key: Optional[str] = None
    gemini_base_url: Optional[str] = None
    gemini_model: str = "gemini-2.0-flash-exp"


@dataclass
class ProcessingConfig:
    """Processing rules configuration."""
    language: str = "auto"
    translate_target: Optional[str] = None
    skip_existing_lyrics: bool = True
    on_failure: str = "skip"  # or 'log_error'


@dataclass
class WhisperConfig:
    """Whisper ASR configuration."""
    model_size: str = "medium"
    device: str = "cpu"  # or "cuda"
    use_vad: bool = True


@dataclass
class CachingConfig:
    """Caching configuration."""
    enabled: bool = True
    ttl: int = 2592000  # 30 days in seconds


@dataclass
class Config:
    """Main configuration class for LyricFlow."""
    api: APIConfig = field(default_factory=APIConfig)
    processing: ProcessingConfig = field(default_factory=ProcessingConfig)
    whisper: WhisperConfig = field(default_factory=WhisperConfig)
    caching: CachingConfig = field(default_factory=CachingConfig)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create Config from dictionary."""
        # Parse API config with nested structure
        api_data = data.get("api", {})
        api_config = APIConfig(
            default_provider=api_data.get("default_provider", "local"),
            openai_api_key=api_data.get("openai", {}).get("api_key"),
            openai_base_url=api_data.get("openai", {}).get("base_url", "https://api.openai.com/v1"),
            openai_model=api_data.get("openai", {}).get("model", "gpt-3.5-turbo"),
            gemini_api_key=api_data.get("gemini", {}).get("api_key"),
            gemini_base_url=api_data.get("gemini", {}).get("base_url"),
            gemini_model=api_data.get("gemini", {}).get("model", "gemini-2.0-flash-exp"),
        )
        
        return cls(
            api=api_config,
            processing=ProcessingConfig(**data.get("processing", {})),
            whisper=WhisperConfig(**data.get("whisper", {})),
            caching=CachingConfig(**data.get("caching", {})),
        )

    @classmethod
    def from_yaml(cls, path: Path) -> "Config":
        """Load configuration from YAML file."""
        if not path.exists():
            return cls()
        
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        
        return cls.from_dict(data)

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from default locations."""
        config = cls()
        
        # Check for config in project root
        project_config = Path("config.yaml")
        if project_config.exists():
            config = cls.from_yaml(project_config)
        else:
            # Check for config in user home directory
            home_config = Path.home() / ".lyricflow" / "config.yaml"
            if home_config.exists():
                config = cls.from_yaml(home_config)
        
        # Override with environment variables if present (these take precedence)
        if os.getenv("OPENAI_API_KEY"):
            config.api.openai_api_key = os.getenv("OPENAI_API_KEY")
        if os.getenv("OPENAI_MODEL"):
            config.api.openai_model = os.getenv("OPENAI_MODEL")
        if os.getenv("GEMINI_API_KEY"):
            config.api.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if os.getenv("GEMINI_MODEL"):
            config.api.gemini_model = os.getenv("GEMINI_MODEL")
        if os.getenv("LYRICFLOW_API_PROVIDER"):
            config.api.default_provider = os.getenv("LYRICFLOW_API_PROVIDER")
        
        return config

    def save(self, path: Path) -> None:
        """Save configuration to YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "api": {
                "default_provider": self.api.default_provider,
                "openai": {
                    "api_key": self.api.openai_api_key or "YOUR_API_KEY_HERE",
                    "base_url": self.api.openai_base_url,
                    "model": self.api.openai_model,
                },
                "gemini": {
                    "api_key": self.api.gemini_api_key or "YOUR_API_KEY_HERE",
                    "base_url": self.api.gemini_base_url,
                    "model": self.api.gemini_model,
                },
            },
            "processing": {
                "language": self.processing.language,
                "translate_target": self.processing.translate_target,
                "skip_existing_lyrics": self.processing.skip_existing_lyrics,
                "on_failure": self.processing.on_failure,
            },
            "whisper": {
                "model_size": self.whisper.model_size,
                "device": self.whisper.device,
                "use_vad": self.whisper.use_vad,
            },
            "caching": {
                "enabled": self.caching.enabled,
                "ttl": self.caching.ttl,
            },
        }
        
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
