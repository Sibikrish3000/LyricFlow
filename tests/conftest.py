"""
Configuration for pytest.
"""
import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp)


@pytest.fixture
def sample_lrc_content():
    """Sample LRC file content."""
    return """[00:12.00]こんにちは世界
[00:15.50]ありがとうございます
[00:20.00]さようなら
"""


@pytest.fixture
def sample_lrc_file(temp_dir, sample_lrc_content):
    """Create a sample LRC file."""
    lrc_file = temp_dir / "test.lrc"
    lrc_file.write_text(sample_lrc_content, encoding="utf-8")
    return lrc_file


@pytest.fixture
def mock_config():
    """Mock configuration for testing."""
    from lyricflow.utils.config import Config, APIConfig, ProcessingConfig
    
    config = Config()
    config.api.default_provider = "local"
    config.processing.skip_existing_lyrics = False
    return config


@pytest.fixture
def test_audio_files():
    """Get test audio files if they exist."""
    test_dir = Path("tests")
    if test_dir.exists():
        return list(test_dir.glob("*.m4a")) + list(test_dir.glob("*.mp3"))
    return []
