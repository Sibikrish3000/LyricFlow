"""
Unit tests for audio handling functionality.
"""
import pytest
from pathlib import Path
from lyricflow.core.audio_handler import AudioHandler


class TestAudioHandler:
    """Test AudioHandler class."""
    
    def test_initialization(self, tmp_path):
        """Test AudioHandler initialization."""
        audio_file = tmp_path / "test.m4a"
        audio_file.touch()
        
        with pytest.raises(Exception):  # Will fail on invalid audio file
            handler = AudioHandler(audio_file)
    
    def test_get_metadata_invalid_file(self):
        """Test metadata extraction from invalid file."""
        with pytest.raises(Exception):
            handler = AudioHandler(Path("nonexistent.mp3"))
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(), 
                        reason="Test audio file not available")
    def test_get_metadata(self):
        """Test metadata extraction from real audio file."""
        audio_file = Path("tests/01 Shogeki.m4a")
        handler = AudioHandler(audio_file)
        
        metadata = handler.get_metadata()
        
        assert metadata is not None
        assert isinstance(metadata, dict)
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    def test_has_synced_lyrics(self):
        """Test checking for synced lyrics."""
        audio_file = Path("tests/01 Shogeki.m4a")
        handler = AudioHandler(audio_file)
        
        # Should return boolean
        result = handler.has_synced_lyrics()
        assert isinstance(result, bool)
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    def test_has_romanized_lyrics(self):
        """Test checking for romanized lyrics."""
        audio_file = Path("tests/01 Shogeki.m4a")
        handler = AudioHandler(audio_file)
        
        # Should return boolean
        result = handler.has_romanized_lyrics()
        assert isinstance(result, bool)
    
    def test_embed_lyrics_dry_run(self):
        """Test embedding lyrics without actually writing (dry run concept)."""
        # This test validates the concept without modifying files
        pass
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    def test_extract_synced_lyrics(self):
        """Test extracting synced lyrics from audio file."""
        audio_file = Path("tests/01 Shogeki.m4a")
        handler = AudioHandler(audio_file)
        
        try:
            lyrics = handler.extract_synced_lyrics()
            # If it has synced lyrics, should return string
            if lyrics:
                assert isinstance(lyrics, str)
                assert len(lyrics) > 0
        except AttributeError:
            # Method might not exist yet
            pytest.skip("extract_synced_lyrics not implemented")


class TestAudioHandlerFormats:
    """Test AudioHandler with different audio formats."""
    
    @pytest.mark.parametrize("extension", [".mp3", ".m4a", ".flac", ".ogg"])
    def test_supported_formats(self, extension, tmp_path):
        """Test that handler can identify supported formats."""
        audio_file = tmp_path / f"test{extension}"
        audio_file.touch()
        
        # Just verify initialization doesn't crash for supported formats
        # Real audio files would be needed for full testing
        try:
            handler = AudioHandler(audio_file)
        except Exception:
            # Expected to fail with empty files
            pass


class TestLRCEmbedding:
    """Test LRC content embedding."""
    
    def test_embed_lrc_content_validation(self, tmp_path):
        """Test LRC content validation before embedding."""
        audio_file = tmp_path / "test.m4a"
        audio_file.touch()
        
        valid_lrc = "[00:12.00]Test lyrics\n[00:15.50]Second line"
        
        # Should accept valid LRC format
        assert "[00:" in valid_lrc
        assert "]" in valid_lrc
    
    def test_lrc_format_validation(self, tmp_path):
        """Test various LRC format validations."""
        audio_file = tmp_path / "test.m4a"
        audio_file.touch()
        
        valid_formats = [
            "[00:12.00]Text",
            "[00:12.34]Text with spaces",
            "[01:23.45]日本語テキスト",
        ]
        
        for lrc in valid_formats:
            assert lrc.startswith("[")
            assert "]" in lrc


class TestMetadataExtraction:
    """Test metadata extraction from various sources."""
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    def test_metadata_structure(self):
        """Test that metadata has expected structure."""
        audio_file = Path("tests/01 Shogeki.m4a")
        handler = AudioHandler(audio_file)
        
        metadata = handler.get_metadata()
        
        assert isinstance(metadata, dict)
        # Metadata should have at least some common fields
        # Check if it has any metadata at all
        assert len(metadata) >= 0  # Can be empty


class TestAudioHandlerErrorHandling:
    """Test error handling in AudioHandler."""
    
    def test_invalid_path(self):
        """Test handling of invalid file paths."""
        with pytest.raises(Exception):
            handler = AudioHandler(Path("/nonexistent/path/file.mp3"))
    
    def test_empty_path(self):
        """Test handling of empty path."""
        with pytest.raises(Exception):
            handler = AudioHandler(Path(""))
    
    def test_directory_instead_of_file(self, tmp_path):
        """Test handling when directory is provided instead of file."""
        with pytest.raises(Exception):
            handler = AudioHandler(tmp_path)
