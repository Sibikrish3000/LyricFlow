"""
Unit tests for configuration management.
"""
import os
import pytest
from pathlib import Path
import tempfile
import yaml

from lyricflow.utils.config import Config, APIConfig, ProcessingConfig, WhisperConfig, CachingConfig


class TestAPIConfig:
    """Test APIConfig dataclass."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = APIConfig()
        assert config.default_provider == "local"
        assert config.openai_model == "gpt-3.5-turbo"
        assert config.gemini_model == "gemini-2.0-flash-exp"
        assert config.openai_base_url == "https://api.openai.com/v1"
        assert config.openai_api_key is None
        assert config.gemini_api_key is None
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = APIConfig(
            default_provider="gemini",
            openai_model="gpt-4",
            gemini_model="gemini-2.5-pro",
            openai_api_key="test-key-openai",
            gemini_api_key="test-key-gemini"
        )
        assert config.default_provider == "gemini"
        assert config.openai_model == "gpt-4"
        assert config.gemini_model == "gemini-2.5-pro"
        assert config.openai_api_key == "test-key-openai"
        assert config.gemini_api_key == "test-key-gemini"


class TestProcessingConfig:
    """Test ProcessingConfig dataclass."""
    
    def test_default_values(self):
        """Test default processing configuration."""
        config = ProcessingConfig()
        assert config.language == "auto"
        assert config.translate_target is None
        assert config.skip_existing_lyrics is True
        assert config.on_failure == "skip"


class TestWhisperConfig:
    """Test WhisperConfig dataclass."""
    
    def test_default_values(self):
        """Test default Whisper configuration."""
        config = WhisperConfig()
        assert config.model_size == "medium"
        assert config.device == "cpu"
        assert config.use_vad is True


class TestCachingConfig:
    """Test CachingConfig dataclass."""
    
    def test_default_values(self):
        """Test default caching configuration."""
        config = CachingConfig()
        assert config.enabled is True
        assert config.ttl == 2592000  # 30 days


class TestConfig:
    """Test main Config class."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = Config()
        assert isinstance(config.api, APIConfig)
        assert isinstance(config.processing, ProcessingConfig)
        assert isinstance(config.whisper, WhisperConfig)
        assert isinstance(config.caching, CachingConfig)
    
    def test_from_dict(self):
        """Test loading configuration from dictionary."""
        data = {
            "api": {
                "default_provider": "gemini",
                "openai": {
                    "api_key": "sk-test",
                    "base_url": "https://custom.openai.com",
                    "model": "gpt-4-turbo"
                },
                "gemini": {
                    "api_key": "gemini-test",
                    "base_url": None,
                    "model": "gemini-2.5-pro"
                }
            },
            "processing": {
                "language": "ja",
                "skip_existing_lyrics": False
            },
            "whisper": {
                "model_size": "large",
                "device": "cuda"
            },
            "caching": {
                "enabled": False,
                "ttl": 3600
            }
        }
        
        config = Config.from_dict(data)
        
        assert config.api.default_provider == "gemini"
        assert config.api.openai_api_key == "sk-test"
        assert config.api.openai_model == "gpt-4-turbo"
        assert config.api.gemini_api_key == "gemini-test"
        assert config.api.gemini_model == "gemini-2.5-pro"
        assert config.processing.language == "ja"
        assert config.processing.skip_existing_lyrics is False
        assert config.whisper.model_size == "large"
        assert config.whisper.device == "cuda"
        assert config.caching.enabled is False
        assert config.caching.ttl == 3600
    
    def test_from_yaml(self, tmp_path):
        """Test loading configuration from YAML file."""
        yaml_content = """
api:
  default_provider: gemini
  openai:
    api_key: "sk-test"
    base_url: "https://api.openai.com/v1"
    model: "gpt-4"
  gemini:
    api_key: "gemini-test"
    base_url: null
    model: "gemini-2.5-pro"

processing:
  language: ja
  skip_existing_lyrics: false

whisper:
  model_size: small
  device: cpu

caching:
  enabled: true
  ttl: 86400
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        
        config = Config.from_yaml(config_file)
        
        assert config.api.default_provider == "gemini"
        assert config.api.openai_model == "gpt-4"
        assert config.api.gemini_model == "gemini-2.5-pro"
        assert config.processing.language == "ja"
        assert config.whisper.model_size == "small"
        assert config.caching.ttl == 86400
    
    def test_env_var_override(self, tmp_path, monkeypatch):
        """Test environment variable override."""
        # Create a config file
        yaml_content = """
api:
  default_provider: local
  openai:
    api_key: "from-file"
    model: "gpt-3.5-turbo"
  gemini:
    api_key: "from-file"
    model: "gemini-2.0-flash-exp"
"""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml_content)
        
        # Change to temp directory so Config.load() finds our config
        monkeypatch.chdir(tmp_path)
        
        # Set environment variables
        monkeypatch.setenv("OPENAI_API_KEY", "from-env")
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4-turbo")
        monkeypatch.setenv("GEMINI_API_KEY", "from-env-gemini")
        monkeypatch.setenv("GEMINI_MODEL", "gemini-2.5-pro")
        monkeypatch.setenv("LYRICFLOW_API_PROVIDER", "gemini")
        
        config = Config.load()
        
        # Environment variables should override file values
        assert config.api.openai_api_key == "from-env"
        assert config.api.openai_model == "gpt-4-turbo"
        assert config.api.gemini_api_key == "from-env-gemini"
        assert config.api.gemini_model == "gemini-2.5-pro"
        assert config.api.default_provider == "gemini"
    
    def test_save_config(self, tmp_path):
        """Test saving configuration to YAML."""
        config = Config()
        config.api.default_provider = "gemini"
        config.api.openai_api_key = "test-key"
        config.api.gemini_model = "gemini-2.5-pro"
        
        config_file = tmp_path / "saved_config.yaml"
        config.save(config_file)
        
        assert config_file.exists()
        
        # Load and verify
        loaded = Config.from_yaml(config_file)
        assert loaded.api.default_provider == "gemini"
        assert loaded.api.gemini_model == "gemini-2.5-pro"
    
    def test_missing_config_file(self, tmp_path, monkeypatch):
        """Test loading when no config file exists."""
        monkeypatch.chdir(tmp_path)
        config = Config.load()
        
        # Should return default values
        assert config.api.default_provider == "local"
        assert config.api.openai_model == "gpt-3.5-turbo"
