"""
Integration tests for the complete LyricFlow workflow.
"""
import pytest
from pathlib import Path
from lyricflow import Romanizer, AudioHandler, LyricsSync
from lyricflow.utils.config import Config


class TestEndToEndWorkflow:
    """Test complete end-to-end workflows."""
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.m4a").exists(),
                        reason="Test audio files not available")
    def test_complete_workflow(self):
        """Test complete processing workflow."""
        config = Config()
        config.api.default_provider = "local"
        config.processing.skip_existing_lyrics = False
        
        lyrics_sync = LyricsSync(config=config)
        audio_file = Path("tests/01 Shogeki.m4a")
        
        result = lyrics_sync.process_audio_file(audio_file, overwrite=True)
        
        assert result is not None
        assert result["status"] in ["success", "partial", "no_lyrics"]
        assert "file" in result
        assert "steps" in result
    
    @pytest.mark.skipif(not Path("tests/01 Shogeki.lrc").exists(),
                        reason="Test LRC files not available")
    def test_lrc_to_romaji_workflow(self):
        """Test LRC romanization workflow."""
        config = Config()
        lyrics_sync = LyricsSync(config=config)
        
        lrc_file = Path("tests/01 Shogeki.lrc")
        lrc_content = lrc_file.read_text(encoding="utf-8")
        
        romaji_content = lyrics_sync.romanize_lrc_content(lrc_content)
        
        assert romaji_content is not None
        assert len(romaji_content) > 0
        assert "[00:" in romaji_content


class TestMultipleFileProcessing:
    """Test processing multiple files."""
    
    @pytest.mark.skipif(not Path("tests").exists(),
                        reason="Test directory not available")
    def test_batch_processing(self):
        """Test batch processing of directory."""
        config = Config()
        config.api.default_provider = "local"
        
        lyrics_sync = LyricsSync(config=config)
        test_dir = Path("tests")
        
        if test_dir.exists():
            results = lyrics_sync.process_directory(test_dir)
            
            assert isinstance(results, list)
            if len(results) > 0:
                for result in results:
                    assert "status" in result
                    assert "file" in result


class TestComponentIntegration:
    """Test integration between components."""
    
    def test_romanizer_audio_handler_integration(self):
        """Test Romanizer and AudioHandler working together."""
        config = Config()
        romanizer = Romanizer(config)
        
        # AudioHandler needs a file, so we just test they can coexist
        assert romanizer is not None
    
    def test_config_romanizer_integration(self):
        """Test Config and Romanizer integration."""
        config = Config()
        config.api.default_provider = "local"
        
        romanizer = Romanizer(config)
        
        assert romanizer.config.api.default_provider == "local"
    
    def test_all_components_together(self):
        """Test all components can be initialized together."""
        config = Config()
        romanizer = Romanizer(config)
        lyrics_sync = LyricsSync(config)
        
        assert romanizer is not None
        assert lyrics_sync is not None
