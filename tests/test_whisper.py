"""
Unit tests for Whisper ASR lyric generation.
"""
import pytest
from pathlib import Path
from lyricflow.core.whisper_gen import (
    WhisperLyricGenerator,
    generate_lyrics_from_audio,
    WHISPER_AVAILABLE
)
from lyricflow.utils.config import WhisperConfig


@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="Whisper not installed")
class TestWhisperLyricGenerator:
    """Test WhisperLyricGenerator class."""
    
    def test_initialization(self):
        """Test Whisper generator initialization."""
        config = WhisperConfig(model_size="tiny", device="cpu")
        generator = WhisperLyricGenerator(config)
        
        assert generator is not None
        assert generator.config.model_size == "tiny"
        assert generator.device in ["cpu", "cuda"]
    
    def test_initialization_default_config(self):
        """Test initialization with default config."""
        generator = WhisperLyricGenerator()
        
        assert generator is not None
        assert generator.config is not None
    
    def test_get_device_cpu(self):
        """Test device selection for CPU."""
        config = WhisperConfig(device="cpu")
        generator = WhisperLyricGenerator(config)
        
        assert generator.device == "cpu"
    
    def test_format_timestamp(self):
        """Test timestamp formatting."""
        # Test various timestamps
        assert WhisperLyricGenerator._format_timestamp(0) == "00:00.00"
        assert WhisperLyricGenerator._format_timestamp(61.5) == "01:01.50"
        assert WhisperLyricGenerator._format_timestamp(125.75) == "02:05.75"
    
    def test_model_not_loaded_initially(self):
        """Test that model is not loaded on initialization."""
        generator = WhisperLyricGenerator()
        assert generator.model is None
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    @pytest.mark.slow
    def test_transcribe_audio(self):
        """Test audio transcription."""
        config = WhisperConfig(model_size="tiny", device="cpu")
        generator = WhisperLyricGenerator(config)
        
        audio_file = Path("tests/01 Shogeki.m4a")
        
        # This is a slow test as it actually runs Whisper
        result = generator.transcribe_audio(audio_file, language="ja")
        
        assert result is not None
        assert "segments" in result or "text" in result
    
    def test_transcribe_nonexistent_file(self):
        """Test transcription of nonexistent file."""
        generator = WhisperLyricGenerator()
        
        with pytest.raises(FileNotFoundError):
            generator.transcribe_audio(Path("nonexistent.mp3"))
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    @pytest.mark.slow
    def test_generate_lrc(self, tmp_path):
        """Test LRC generation."""
        config = WhisperConfig(model_size="tiny", device="cpu")
        generator = WhisperLyricGenerator(config)
        
        audio_file = Path("tests/01 Shogeki.m4a")
        output_file = tmp_path / "generated.lrc"
        
        lrc_content = generator.generate_lrc(audio_file, language="ja", output_path=output_file)
        
        assert lrc_content is not None
        assert len(lrc_content) > 0
        assert "[00:" in lrc_content or "[01:" in lrc_content
        assert output_file.exists()


@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="Whisper not installed")
class TestWhisperConfig:
    """Test Whisper configuration."""
    
    def test_default_config(self):
        """Test default Whisper configuration."""
        config = WhisperConfig()
        
        assert config.model_size == "medium"
        assert config.device == "cpu"
        assert config.use_vad is True
    
    def test_custom_config(self):
        """Test custom Whisper configuration."""
        config = WhisperConfig(
            model_size="large",
            device="cuda",
            use_vad=False
        )
        
        assert config.model_size == "large"
        assert config.device == "cuda"
        assert config.use_vad is False


@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="Whisper not installed")
class TestConvenienceFunction:
    """Test convenience function."""
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    @pytest.mark.slow
    def test_generate_lyrics_from_audio(self, tmp_path):
        """Test convenience function for lyric generation."""
        audio_file = Path("tests/01 Shogeki.m4a")
        output_file = tmp_path / "generated.lrc"
        
        lrc_content = generate_lyrics_from_audio(
            audio_file,
            output_path=output_file,
            language="ja",
            model_size="tiny",
            device="cpu"
        )
        
        assert lrc_content is not None
        assert len(lrc_content) > 0
        assert output_file.exists()
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    @pytest.mark.slow
    def test_generate_word_level_lyrics(self, tmp_path):
        """Test word-level lyric generation."""
        audio_file = Path("tests/01 Shogeki.m4a")
        output_file = tmp_path / "generated_word.lrc"
        
        lrc_content = generate_lyrics_from_audio(
            audio_file,
            output_path=output_file,
            language="ja",
            model_size="tiny",
            device="cpu",
            word_level=True
        )
        
        assert lrc_content is not None
        assert len(lrc_content) > 0


class TestWhisperImportError:
    """Test behavior when Whisper is not installed."""
    
    @pytest.mark.skipif(WHISPER_AVAILABLE, reason="Whisper is installed")
    def test_import_error(self):
        """Test that ImportError is raised when Whisper not installed."""
        with pytest.raises(ImportError):
            generator = WhisperLyricGenerator()


class TestTimestampFormatting:
    """Test timestamp formatting edge cases."""
    
    def test_zero_timestamp(self):
        """Test formatting of zero timestamp."""
        result = WhisperLyricGenerator._format_timestamp(0.0)
        assert result == "00:00.00"
    
    def test_sub_second_timestamp(self):
        """Test formatting of sub-second timestamps."""
        result = WhisperLyricGenerator._format_timestamp(0.5)
        assert result == "00:00.50"
    
    def test_minute_boundary(self):
        """Test formatting at minute boundaries."""
        result = WhisperLyricGenerator._format_timestamp(60.0)
        assert result == "01:00.00"
    
    def test_large_timestamp(self):
        """Test formatting of large timestamps."""
        result = WhisperLyricGenerator._format_timestamp(3661.25)  # 1 hour, 1 minute, 1.25 seconds
        assert result == "61:01.25"
    
    def test_precise_timestamp(self):
        """Test formatting with precise decimals."""
        result = WhisperLyricGenerator._format_timestamp(123.456)
        assert result == "02:03.46"  # Should round to 2 decimal places


@pytest.mark.skipif(not WHISPER_AVAILABLE, reason="Whisper not installed")
class TestVAD:
    """Test Voice Activity Detection."""
    
    def test_vad_config_enabled(self):
        """Test VAD configuration."""
        config = WhisperConfig(use_vad=True)
        generator = WhisperLyricGenerator(config)
        
        assert generator.config.use_vad is True
    
    def test_vad_config_disabled(self):
        """Test VAD disabled."""
        config = WhisperConfig(use_vad=False)
        generator = WhisperLyricGenerator(config)
        
        assert generator.config.use_vad is False
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    def test_apply_vad(self):
        """Test VAD application."""
        generator = WhisperLyricGenerator()
        audio_file = Path("tests/01 Shogeki.m4a")
        
        # Currently returns empty list (not implemented)
        segments = generator.apply_vad(audio_file)
        assert isinstance(segments, list)
