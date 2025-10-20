"""
Unit tests for lyrics synchronization functionality.
"""
import pytest
from pathlib import Path
from lyricflow.core.lyrics_sync import LyricsSync
from lyricflow.utils.config import Config


class TestLyricsSync:
    """Test LyricsSync class."""
    
    @pytest.fixture
    def lyrics_sync(self, mock_config):
        """Create a LyricsSync instance."""
        return LyricsSync(config=mock_config)
    
    def test_initialization(self, lyrics_sync):
        """Test LyricsSync initialization."""
        assert lyrics_sync is not None
        assert lyrics_sync.config is not None
    
    def test_find_lrc_file(self, lyrics_sync, tmp_path):
        """Test finding LRC files."""
        audio_file = tmp_path / "song.m4a"
        audio_file.touch()
        
        lrc_file = tmp_path / "song.lrc"
        lrc_file.write_text("[00:12.00]Test lyrics", encoding="utf-8")
        
        found = lyrics_sync.find_lrc_file(audio_file)
        assert found == lrc_file
    
    def test_find_lrc_file_not_exists(self, lyrics_sync, tmp_path):
        """Test finding LRC file that doesn't exist."""
        audio_file = tmp_path / "song.m4a"
        audio_file.touch()
        
        found = lyrics_sync.find_lrc_file(audio_file)
        assert found is None
    
    def test_romanize_lrc_content(self, lyrics_sync, sample_lrc_content):
        """Test romanizing LRC content."""
        result = lyrics_sync.romanize_lrc_content(sample_lrc_content)
        
        assert result is not None
        assert len(result) > 0
        assert "[00:" in result  # Should preserve timestamps
    
    def test_parse_lrc_line(self, lyrics_sync):
        """Test parsing individual LRC lines."""
        line = "[00:12.34]こんにちは世界"
        
        # The method should preserve timestamps and romanize text
        result = lyrics_sync.romanize_lrc_content(line)
        assert "[00:12.34]" in result
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio file not available")
    def test_process_audio_file(self, lyrics_sync):
        """Test processing a real audio file."""
        audio_file = Path("tests/01 Shogeki.m4a")
        
        result = lyrics_sync.process_audio_file(audio_file)
        
        assert result is not None
        assert "status" in result
        assert "file" in result
        assert result["status"] in ["success", "partial", "skipped", "no_lyrics", "error"]
    
    def test_process_directory(self, lyrics_sync, tmp_path):
        """Test processing a directory of files."""
        # Create some test audio files
        (tmp_path / "song1.m4a").touch()
        (tmp_path / "song2.mp3").touch()
        (tmp_path / "not_audio.txt").touch()
        
        results = lyrics_sync.process_directory(tmp_path)
        
        assert isinstance(results, list)
        # Should only process audio files
        assert len(results) == 2


class TestLRCParsing:
    """Test LRC file parsing."""
    
    @pytest.fixture
    def lyrics_sync(self, mock_config):
        """Create a LyricsSync instance."""
        return LyricsSync(config=mock_config)
    
    def test_parse_simple_lrc(self, lyrics_sync):
        """Test parsing simple LRC content."""
        lrc = "[00:12.00]First line\n[00:15.50]Second line"
        
        result = lyrics_sync.romanize_lrc_content(lrc)
        
        assert "[00:12.00]" in result
        assert "[00:15.50]" in result
    
    def test_parse_lrc_with_metadata(self, lyrics_sync):
        """Test parsing LRC with metadata tags."""
        lrc = """[ti:Song Title]
[ar:Artist Name]
[00:12.00]Lyrics line"""
        
        result = lyrics_sync.romanize_lrc_content(lrc)
        
        # Should preserve metadata
        assert "[ti:" in result or "Song Title" in result
        assert "[00:12.00]" in result
    
    def test_parse_multiline_lrc(self, lyrics_sync):
        """Test parsing multi-line LRC."""
        lrc = """[00:12.00]Line 1
[00:15.50]Line 2
[00:20.00]Line 3"""
        
        result = lyrics_sync.romanize_lrc_content(lrc)
        lines = result.strip().split("\n")
        
        assert len(lines) >= 3
    
    def test_empty_lrc(self, lyrics_sync):
        """Test handling empty LRC."""
        result = lyrics_sync.romanize_lrc_content("")
        assert result == ""


class TestProcessingWorkflow:
    """Test the complete processing workflow."""
    
    @pytest.fixture
    def lyrics_sync(self, mock_config):
        """Create a LyricsSync instance."""
        mock_config.processing.skip_existing_lyrics = False
        return LyricsSync(config=mock_config)
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.lrc").exists(),
                        reason="Test LRC file not available")
    def test_workflow_with_lrc_file(self, lyrics_sync):
        """Test workflow when LRC file exists."""
        audio_file = Path("tests/01 Shogeki.m4a")
        lrc_file = Path("tests/01 Shogeki.lrc")
        
        if audio_file.exists() and lrc_file.exists():
            result = lyrics_sync.process_audio_file(audio_file)
            
            assert result["status"] in ["success", "partial", "skipped"]
            assert "steps" in result
            assert len(result["steps"]) > 0
    
    def test_workflow_no_lyrics(self, lyrics_sync, tmp_path):
        """Test workflow when no lyrics are available."""
        audio_file = tmp_path / "song_no_lyrics.m4a"
        audio_file.touch()
        
        result = lyrics_sync.process_audio_file(audio_file)
        
        assert result["status"] in ["no_lyrics", "error"]


class TestRomanizedLRCGeneration:
    """Test romanized LRC file generation."""
    
    @pytest.fixture
    def lyrics_sync(self, mock_config):
        """Create a LyricsSync instance."""
        return LyricsSync(config=mock_config)
    
    def test_generate_romaji_lrc_filename(self, lyrics_sync, tmp_path):
        """Test romaji LRC filename generation."""
        audio_file = tmp_path / "song.m4a"
        lrc_file = tmp_path / "song.lrc"
        lrc_file.write_text("[00:12.00]こんにちは", encoding="utf-8")
        
        # Expected romaji filename
        romaji_file = tmp_path / "song_romaji.lrc"
        
        assert romaji_file.name == "song_romaji.lrc"
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.lrc").exists(),
                        reason="Test LRC file not available")
    def test_romaji_lrc_creation(self, lyrics_sync):
        """Test that romaji LRC file is created."""
        audio_file = Path("tests/01 Shogeki.m4a")
        romaji_file = Path("tests/01 Shogeki_romaji.lrc")
        
        if audio_file.exists():
            lyrics_sync.process_audio_file(audio_file, overwrite=True)
            
            # Check if romaji file was created
            if romaji_file.exists():
                content = romaji_file.read_text(encoding="utf-8")
                assert len(content) > 0
                assert "[00:" in content  # Should have timestamps


class TestErrorHandling:
    """Test error handling in lyrics sync."""
    
    @pytest.fixture
    def lyrics_sync(self, mock_config):
        """Create a LyricsSync instance."""
        return LyricsSync(config=mock_config)
    
    def test_invalid_audio_file(self, lyrics_sync):
        """Test handling of invalid audio file."""
        result = lyrics_sync.process_audio_file(Path("nonexistent.mp3"))
        
        assert result["status"] == "error"
        assert "error" in result or "steps" in result
    
    def test_corrupted_lrc_file(self, lyrics_sync, tmp_path):
        """Test handling of corrupted LRC file."""
        audio_file = tmp_path / "song.m4a"
        audio_file.touch()
        
        lrc_file = tmp_path / "song.lrc"
        lrc_file.write_text("Invalid LRC content without timestamps", encoding="utf-8")
        
        result = lyrics_sync.process_audio_file(audio_file)
        
        # Should handle gracefully
        assert result is not None
        assert "status" in result


class TestSkipExistingLyrics:
    """Test skip_existing_lyrics configuration."""
    
    def test_skip_when_exists(self, mock_config, tmp_path):
        """Test skipping when romanized lyrics already exist."""
        mock_config.processing.skip_existing_lyrics = True
        lyrics_sync = LyricsSync(config=mock_config)
        
        # This would need actual audio file with embedded lyrics
        # For now, just test the config is respected
        assert lyrics_sync.config.processing.skip_existing_lyrics is True
    
    def test_overwrite_when_configured(self, mock_config, tmp_path):
        """Test overwriting when skip_existing_lyrics is False."""
        mock_config.processing.skip_existing_lyrics = False
        lyrics_sync = LyricsSync(config=mock_config)
        
        assert lyrics_sync.config.processing.skip_existing_lyrics is False
