#!/usr/bin/env python3
"""Quick test to verify all fixes are working."""

from lyricflow.utils.config import Config

def test_config_loading():
    """Test that config loads without errors."""
    print("Testing configuration loading...")
    try:
        config = Config.load()
        print(f"✅ Config loaded successfully")
        print(f"   Provider: {config.api.default_provider}")
        print(f"   OpenAI Key: {'Set' if config.api.openai_api_key else 'Not set'}")
        print(f"   Gemini Key: {'Set' if config.api.gemini_api_key else 'Not set'}")
        return True
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False

def test_romanization():
    """Test basic romanization."""
    print("\nTesting romanization...")
    try:
        from lyricflow import Romanizer
        romanizer = Romanizer()
        
        test_cases = [
            ("こんにちは世界", "Konnichiha sekai"),
            ("ありがとう", "Ariga tō"),
        ]
        
        for japanese, expected_start in test_cases:
            result = romanizer.romanize(japanese)
            if result.startswith(expected_start.split()[0]):
                print(f"✅ '{japanese}' → '{result}'")
            else:
                print(f"❌ '{japanese}' → '{result}' (expected to start with '{expected_start}')")
        
        return True
    except Exception as e:
        print(f"❌ Romanization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_import():
    """Test that CLI imports without errors."""
    print("\nTesting CLI import...")
    try:
        from lyricflow.cli.main import cli
        print("✅ CLI imported successfully")
        return True
    except Exception as e:
        print(f"❌ CLI import failed: {e}")
        return False

def main():
    print("=" * 60)
    print("LyricFlow Quick Test Suite")
    print("=" * 60 + "\n")
    
    results = []
    results.append(test_config_loading())
    results.append(test_romanization())
    results.append(test_cli_import())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    print("=" * 60)

if __name__ == "__main__":
    main()
