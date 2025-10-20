#!/usr/bin/env python3
"""
Quick test script for LyricFlow functionality.
"""

from pathlib import Path
from lyricflow import LyricsSync, Romanizer, AudioHandler

def test_romanization():
    """Test basic romanization."""
    print("=" * 60)
    print("Testing Romanization")
    print("=" * 60)
    
    romanizer = Romanizer()
    test_texts = [
        "こんにちは世界",
        "ありがとうございます",
        "私の名前は太郎です",
    ]
    
    for text in test_texts:
        result = romanizer.romanize(text)
        print(f"{text} → {result}")
    print()

def test_audio_processing():
    """Test audio file processing."""
    print("=" * 60)
    print("Testing Audio Processing")
    print("=" * 60)
    
    # Find test audio files
    test_dir = Path("tests")
    if not test_dir.exists():
        print("No tests directory found")
        return
    
    audio_files = list(test_dir.glob("*.m4a")) + list(test_dir.glob("*.mp3"))
    
    if not audio_files:
        print("No audio files found in tests directory")
        return
    
    lyrics_sync = LyricsSync()
    
    for audio_file in audio_files[:2]:  # Test first 2 files
        print(f"\nProcessing: {audio_file.name}")
        result = lyrics_sync.process_audio_file(
            audio_file,
            use_ai=False,
            overwrite=True,  # Force reprocess for testing
            no_embed=False
        )
        
        print(f"Status: {result['status'].upper()}")
        for step in result['steps']:
            print(f"  • {step}")
    print()

def test_audio_metadata():
    """Test audio metadata reading."""
    print("=" * 60)
    print("Testing Audio Metadata Reading")
    print("=" * 60)
    
    test_dir = Path("tests")
    if not test_dir.exists():
        return
    
    audio_files = list(test_dir.glob("*.m4a")) + list(test_dir.glob("*.mp3"))
    
    for audio_file in audio_files[:2]:
        try:
            audio = AudioHandler(audio_file)
            metadata = audio.get_metadata()
            
            print(f"\n{audio_file.name}:")
            print(f"  Title:  {metadata.get('title', 'N/A')}")
            print(f"  Artist: {metadata.get('artist', 'N/A')}")
            print(f"  Album:  {metadata.get('album', 'N/A')}")
            print(f"  Has Romanized: {audio.has_romanized_lyrics()}")
        except Exception as e:
            print(f"Error reading {audio_file.name}: {e}")
    print()

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("LyricFlow Test Suite")
    print("=" * 60 + "\n")
    
    try:
        test_romanization()
        test_audio_metadata()
        test_audio_processing()
        
        print("=" * 60)
        print("All tests completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
