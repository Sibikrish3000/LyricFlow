"""
Unit tests for romanization functionality.
"""
import pytest
from lyricflow.core.romanizer import LocalRomanizer, AIRomanizer, Romanizer, LOCAL_ROMANIZATION_AVAILABLE
from lyricflow.utils.config import Config


@pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="pykakasi/fugashi not available")
class TestLocalRomanizer:
    """Test local romanization using pykakasi and fugashi."""
    
    @pytest.fixture
    def romanizer(self):
        """Create a LocalRomanizer instance."""
        return LocalRomanizer()
    
    def test_basic_romanization(self, romanizer):
        """Test basic Japanese romanization."""
        tests = [
            ("こんにちは", ["konnichiwa", "konnichiha"]),  # Both are valid
            ("ありがとう", ["arigatō", "arigatou", "arigato"]),
            ("世界", ["sekai"]),
        ]
        
        for japanese, expected_variants in tests:
            result = romanizer.romanize(japanese).lower()
            # Normalize macrons and check if any variant matches
            result_normalized = result.replace("ō", "o").replace("ū", "u").replace(" ", "")
            expected_normalized = [e.replace("ō", "o").replace("ū", "u").replace(" ", "") for e in expected_variants]
            assert any(exp in result_normalized for exp in expected_normalized), \
                f"Expected one of {expected_variants}, got {result}"
    
    def test_particle_conversion(self, romanizer):
        """Test correct particle romanization."""
        tests = [
            ("私は学生です", "wa"),  # は should be 'wa'
            ("本を読む", "o"),      # を should be 'o'
            ("学校へ行く", "e"),    # へ should be 'e'
        ]
        
        for japanese, expected_particle in tests:
            result = romanizer.romanize(japanese).lower()
            assert expected_particle in result
    
    def test_long_text(self, romanizer):
        """Test romanization of longer text."""
        text = "一秒前の瞬き取り残された世界"
        result = romanizer.romanize(text)
        
        assert len(result) > 0
        # Allow macrons (ō, ū) which are common in romanization
        # Remove macrons before checking ASCII
        ascii_result = result.replace("ō", "o").replace("ū", "u").replace("ā", "a").replace("ē", "e").replace("ī", "i")
        assert ascii_result.replace(" ", "").isascii(), f"Non-ASCII characters found in: {result}"
    
    def test_empty_string(self, romanizer):
        """Test romanization of empty string."""
        result = romanizer.romanize("")
        assert result == ""
    
    def test_mixed_content(self, romanizer):
        """Test romanization of mixed Japanese and English."""
        text = "こんにちは world"
        result = romanizer.romanize(text)
        assert "world" in result.lower()
    
    def test_spacing(self, romanizer):
        """Test that spacing is applied properly."""
        text = "私の名前は太郎です"
        result = romanizer.romanize(text)
        
        # Should have spaces between words
        assert " " in result


class TestAIRomanizer:
    """Test AI-based romanization (mocked)."""
    
    def test_initialization_openai(self):
        """Test OpenAI romanizer initialization."""
        try:
            romanizer = AIRomanizer(
                provider="openai",
                api_key="test-key",
                base_url="https://api.openai.com/v1",
                model="gpt-3.5-turbo"
            )
            assert romanizer.provider == "openai"
            assert romanizer.model == "gpt-3.5-turbo"
            assert romanizer.api_key == "test-key"
        except ImportError:
            pytest.skip("OpenAI library not available")
    
    def test_initialization_gemini(self):
        """Test Gemini romanizer initialization."""
        romanizer = AIRomanizer(
            provider="gemini",
            api_key="test-key",
            model="gemini-2.5-pro"
        )
        assert romanizer.provider == "gemini"
        assert romanizer.model == "gemini-2.5-pro"
        assert romanizer.api_key == "test-key"
    
    def test_model_default_values(self):
        """Test default model values."""
        romanizer_gemini = AIRomanizer(
            provider="gemini",
            api_key="test-key"
        )
        assert romanizer_gemini.model == "gemini-2.0-flash-exp"


class TestRomanizer:
    """Test main Romanizer class with fallback."""
    
    def test_initialization_local(self, mock_config):
        """Test Romanizer initialization with local provider."""
        mock_config.api.default_provider = "local"
        romanizer = Romanizer(mock_config)
        
        assert romanizer.config.api.default_provider == "local"
        if LOCAL_ROMANIZATION_AVAILABLE:
            assert romanizer.local_romanizer is not None
    
    def test_initialization_gemini(self, mock_config):
        """Test Romanizer initialization with Gemini provider."""
        mock_config.api.default_provider = "gemini"
        mock_config.api.gemini_api_key = "test-key"
        mock_config.api.gemini_model = "gemini-2.5-pro"
        
        romanizer = Romanizer(mock_config)
        
        assert romanizer.config.api.default_provider == "gemini"
        if romanizer.ai_romanizer:
            assert romanizer.ai_romanizer.model == "gemini-2.5-pro"
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_romanize_local(self, mock_config):
        """Test romanization using local romanizer."""
        mock_config.api.default_provider = "local"
        romanizer = Romanizer(mock_config)
        
        result = romanizer.romanize("こんにちは", use_ai=False)
        assert len(result) > 0
        assert result.replace(" ", "").isascii()
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_fallback_to_local(self, mock_config):
        """Test fallback to local romanization when AI fails."""
        mock_config.api.default_provider = "gemini"
        mock_config.api.gemini_api_key = "invalid-key"
        
        romanizer = Romanizer(mock_config)
        
        # Should fall back to local romanization
        result = romanizer.romanize("こんにちは", use_ai=True)
        assert len(result) > 0
    
    def test_language_parameter(self, mock_config):
        """Test language parameter handling."""
        mock_config.api.default_provider = "local"
        romanizer = Romanizer(mock_config)
        
        # Japanese should work
        if LOCAL_ROMANIZATION_AVAILABLE:
            result = romanizer.romanize("こんにちは", language="ja")
            assert len(result) > 0


class TestRomanizationEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_special_characters(self):
        """Test romanization with special characters."""
        romanizer = LocalRomanizer()
        
        tests = [
            ("こんにちは！", ["konnichiwa", "konnichiha"]),  # Both valid
            ("ありがとう。", ["arigatō", "arigatou", "arigato"]),
            ("「世界」", ["sekai"]),
        ]
        
        for text, expected_variants in tests:
            result = romanizer.romanize(text).lower()
            # Remove macrons and spaces for comparison
            result_normalized = result.replace("ō", "o").replace("ū", "u").replace(" ", "")
            expected_normalized = [e.replace("ō", "o").replace("ū", "u").replace(" ", "") for e in expected_variants]
            assert any(exp in result_normalized for exp in expected_normalized), \
                f"Expected one of {expected_variants} in {result}"
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_numbers(self):
        """Test romanization with numbers."""
        romanizer = LocalRomanizer()
        result = romanizer.romanize("2025年")
        
        assert "2025" in result or "nen" in result.lower()
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_kanji_only(self):
        """Test romanization of kanji-only text."""
        romanizer = LocalRomanizer()
        result = romanizer.romanize("日本語")
        
        assert len(result) > 0
        assert result.replace(" ", "").isascii()
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_hiragana_only(self):
        """Test romanization of hiragana-only text."""
        romanizer = LocalRomanizer()
        result = romanizer.romanize("ひらがな")
        
        assert len(result) > 0
        # Allow for spacing variations (hiragana vs hiraga na)
        result_no_spaces = result.lower().replace(" ", "")
        assert "hiragana" in result_no_spaces, f"Expected 'hiragana' in {result}"
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_katakana_only(self):
        """Test romanization of katakana-only text."""
        romanizer = LocalRomanizer()
        result = romanizer.romanize("カタカナ")
        
        assert len(result) > 0
        assert "katakana" in result.lower()


class TestRomanizationConsistency:
    """Test consistency of romanization."""
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_consistency(self):
        """Test that same input produces same output."""
        romanizer = LocalRomanizer()
        text = "こんにちは世界"
        
        result1 = romanizer.romanize(text)
        result2 = romanizer.romanize(text)
        
        assert result1 == result2
    
    @pytest.mark.skipif(not LOCAL_ROMANIZATION_AVAILABLE, reason="Local romanization not available")
    def test_multiple_calls(self):
        """Test multiple romanization calls."""
        romanizer = LocalRomanizer()
        
        texts = [
            "こんにちは",
            "ありがとう",
            "さようなら",
        ]
        
        for text in texts:
            result = romanizer.romanize(text)
            assert len(result) > 0
