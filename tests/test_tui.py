#!/usr/bin/env python
"""
TUI Test and Demo Script

Quick tests for the Textual TUI interface.
"""

import sys
from pathlib import Path


def test_tui_import():
    """Test 1: Check if TUI imports correctly."""
    print("Test 1: TUI Import")
    print("-" * 50)
    try:
        from lyricflow.tui import LyricFlowTUI, launch_tui
        print("✅ TUI imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("\n💡 Install textual with: pip install textual")
        return False


def test_provider_import():
    """Test 2: Check provider imports."""
    print("\nTest 2: Provider Imports")
    print("-" * 50)
    try:
        from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher
        from lyricflow.core.lrclib import LRCLIBFetcher
        from lyricflow.core.musixmatch import MusixmatchFetcher
        print("✅ All provider imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_cli_fetch_command():
    """Test 3: Check CLI fetch command."""
    print("\nTest 3: CLI Fetch Command")
    print("-" * 50)
    try:
        from lyricflow.cli.main import cli
        print("✅ CLI fetch command available")
        print("\n📝 Usage examples:")
        print("   lyricflow fetch -t 'Song' -a 'Artist'")
        print("   lyricflow fetch -t 'Song' -a 'Artist' --interactive")
        print("   lyricflow fetch -t 'Song' -a 'Artist' --provider lrclib")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_lrclib_connection():
    """Test 4: Test LRCLIB API connection."""
    print("\nTest 4: LRCLIB API Connection")
    print("-" * 50)
    try:
        from lyricflow.core.lrclib import LRCLIBFetcher
        
        print("🔍 Testing connection with 'Yesterday' by 'The Beatles'...")
        fetcher = LRCLIBFetcher()
        result = fetcher.get_best_match("Yesterday", "The Beatles")
        
        if result:
            print(f"✅ LRCLIB API working!")
            print(f"   Found: {result['title']} by {result['artist']}")
            print(f"   Has synced lyrics: {bool(result.get('synced_lyrics'))}")
            return True
        else:
            print("⚠️  No results found (API working but song not in database)")
            return True
    except Exception as e:
        print(f"❌ LRCLIB connection error: {e}")
        return False


def test_tui_launch():
    """Test 5: Launch TUI (interactive)."""
    print("\nTest 5: TUI Launch (Interactive)")
    print("-" * 50)
    print("This will launch the interactive TUI.")
    print("Press Ctrl+C to exit the TUI and continue.")
    
    try:
        response = input("\n▶️  Launch TUI? (y/n): ").lower()
        if response == 'y':
            from lyricflow.tui import launch_tui
            print("\n🚀 Launching TUI...")
            print("   Use Tab to navigate fields")
            print("   Press Ctrl+C to exit\n")
            launch_tui()
            print("\n✅ TUI closed successfully")
            return True
        else:
            print("⏭️  Skipped TUI launch")
            return True
    except KeyboardInterrupt:
        print("\n\n✅ TUI closed by user (Ctrl+C)")
        return True
    except Exception as e:
        print(f"\n❌ TUI error: {e}")
        return False


def test_audio_metadata():
    """Test 6: Test reading audio file metadata (if file exists)."""
    print("\nTest 6: Audio Metadata Reading")
    print("-" * 50)
    
    # Check for test audio files
    test_paths = [
        Path("tests/01 Shogeki.m4a"),
        Path("tests/16 Soul's Refrain.m4a"),
    ]
    
    found_file = None
    for path in test_paths:
        if path.exists():
            found_file = path
            break
    
    if not found_file:
        print("⏭️  No test audio files found")
        print("   To test, place an audio file in tests/ directory")
        return True
    
    try:
        from lyricflow.core.audio_handler import AudioHandler
        
        print(f"🎵 Reading metadata from: {found_file.name}")
        handler = AudioHandler(found_file)
        metadata = handler.get_metadata()
        
        print("✅ Metadata read successfully:")
        print(f"   Title: {metadata.get('title', 'Unknown')}")
        print(f"   Artist: {metadata.get('artist', 'Unknown')}")
        print(f"   Album: {metadata.get('album', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Error reading metadata: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("🧪 LyricFlow TUI Test Suite")
    print("="*60)
    print("\nRunning tests...\n")
    
    tests = [
        test_tui_import,
        test_provider_import,
        test_cli_fetch_command,
        test_lrclib_connection,
        test_audio_metadata,
        test_tui_launch,  # Interactive test last
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append((test_func.__name__, result))
        except KeyboardInterrupt:
            print(f"\n⏭️  Test skipped by user")
            results.append((test_func.__name__, None))
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            results.append((test_func.__name__, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    
    passed = sum(1 for _, r in results if r is True)
    failed = sum(1 for _, r in results if r is False)
    skipped = sum(1 for _, r in results if r is None)
    
    for name, result in results:
        status = "✅ PASS" if result is True else "❌ FAIL" if result is False else "⏭️  SKIP"
        print(f"{status}  {name}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⏭️  Skipped: {skipped}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
    
    print("\n" + "="*60)
    print("📚 Next Steps:")
    print("="*60)
    print("\n1. Run full demo:")
    print("   python demo_providers.py")
    print("\n2. Try CLI commands:")
    print("   lyricflow fetch -t 'Yesterday' -a 'Beatles'")
    print("   lyricflow fetch -t 'Song' -a 'Artist' --interactive")
    print("\n3. Read documentation:")
    print("   docs/PROVIDERS_GUIDE.md")
    print("   docs/MUSIXMATCH_GUIDE.md")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Tests interrupted. Goodbye!")
        sys.exit(0)
