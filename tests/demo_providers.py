#!/usr/bin/env python
"""
LyricFlow Multi-Provider Demo Script

Demonstrates all the features of the multi-provider lyrics fetching system.
"""

from pathlib import Path
from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher, create_fetcher
from lyricflow.core.lrclib import LRCLIBFetcher
from lyricflow.core.musixmatch import MusixmatchFetcher
import logging

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def demo_lrclib():
    """Demo 1: Using LRCLIB (free provider)."""
    print("\n" + "="*60)
    print("DEMO 1: LRCLIB Provider (Free)")
    print("="*60)
    
    fetcher = UnifiedLyricsFetcher(provider="lrclib")
    
    print(f"\n📌 Provider: {fetcher.provider_name}")
    print(f"   Free: {fetcher.is_free}")
    print(f"   Supports Translation: {fetcher.supports_translation}")
    
    print("\n🔍 Searching for: Yesterday by The Beatles")
    result = fetcher.fetch("Yesterday", "The Beatles")
    
    if result:
        print("\n✅ Found!")
        print(f"   Title: {result['title']}")
        print(f"   Artist: {result['artist']}")
        print(f"   Album: {result['album']}")
        print(f"   Duration: {int(result['duration']) // 60}:{int(result['duration']) % 60:02d}")
        print(f"   Has Synced: {result['has_synced']}")
        print(f"   Has Plain: {result['has_plain']}")
        
        # Show preview
        lyrics = result['synced_lyrics'] or result['plain_lyrics']
        if lyrics:
            lines = lyrics.split('\n')[:5]
            print(f"\n📄 Preview (first 5 lines):")
            for line in lines:
                print(f"   {line}")
            print("   ...")
        
        # Save to file
        output_path = Path("demo_lrclib.lrc")
        if fetcher.save_lrc(result, output_path):
            print(f"\n💾 Saved to: {output_path}")
    else:
        print("❌ Not found")


def demo_musixmatch():
    """Demo 2: Using Musixmatch."""
    print("\n" + "="*60)
    print("DEMO 2: Musixmatch Provider")
    print("="*60)
    
    fetcher = UnifiedLyricsFetcher(provider="musixmatch")
    
    print(f"\n📌 Provider: {fetcher.provider_name}")
    print(f"   Free: {fetcher.is_free}")
    print(f"   Supports Translation: {fetcher.supports_translation}")
    
    print("\n🔍 Searching for: Bohemian Rhapsody by Queen")
    result = fetcher.fetch("Bohemian Rhapsody", "Queen")
    
    if result:
        print("\n✅ Found!")
        print(f"   Title: {result['title']}")
        print(f"   Artist: {result['artist']}")
        print(f"   Rating: {result.get('rating', 'N/A')}")
        print(f"   Has Synced: {result['has_synced']}")
        
        # Show preview
        lyrics = result['synced_lyrics'] or result['plain_lyrics']
        if lyrics:
            lines = lyrics.split('\n')[:5]
            print(f"\n📄 Preview (first 5 lines):")
            for line in lines:
                print(f"   {line}")
            print("   ...")
    else:
        print("❌ Not found")


def demo_factory():
    """Demo 3: Using factory function."""
    print("\n" + "="*60)
    print("DEMO 3: Factory Function (Auto-selects Free)")
    print("="*60)
    
    # This will automatically use LRCLIB (free provider)
    fetcher = create_fetcher(prefer_free=True)
    
    print(f"\n📌 Auto-selected: {fetcher.provider_name}")
    print(f"   Free: {fetcher.is_free}")
    
    print("\n🔍 Searching for: Imagine by John Lennon")
    result = fetcher.fetch("Imagine", "John Lennon")
    
    if result:
        print(f"\n✅ Found on {result['provider'].upper()}!")
        print(f"   Title: {result['title']}")
    else:
        print("❌ Not found")


def demo_fallback():
    """Demo 4: Fallback strategy."""
    print("\n" + "="*60)
    print("DEMO 4: Fallback Strategy")
    print("="*60)
    
    def fetch_with_fallback(title, artist):
        """Try LRCLIB first, fallback to Musixmatch."""
        
        # Try LRCLIB (free)
        print(f"\n🔍 Trying LRCLIB for: {title} by {artist}")
        fetcher = UnifiedLyricsFetcher(provider="lrclib")
        result = fetcher.fetch(title, artist)
        
        if result:
            print(f"   ✅ Found on LRCLIB!")
            return result
        
        # Fallback to Musixmatch
        print("   ⚠️  Not found on LRCLIB, trying Musixmatch...")
        fetcher = UnifiedLyricsFetcher(provider="musixmatch")
        result = fetcher.fetch(title, artist)
        
        if result:
            print(f"   ✅ Found on Musixmatch!")
            return result
        
        print("   ❌ Not found on any provider")
        return None
    
    # Test with a song
    result = fetch_with_fallback("Let It Be", "The Beatles")
    if result:
        print(f"\n📊 Final Result:")
        print(f"   Provider: {result['provider'].upper()}")
        print(f"   Title: {result['title']}")


def demo_romanization():
    """Demo 5: With romanization."""
    print("\n" + "="*60)
    print("DEMO 5: Romanization Support")
    print("="*60)
    
    fetcher = UnifiedLyricsFetcher(provider="lrclib")
    
    print("\n🔍 Searching for: Senbonzakura by Hatsune Miku")
    result = fetcher.fetch(
        "千本桜",
        "初音ミク",
        fetch_romanization=True
    )
    
    if result:
        print("\n✅ Found!")
        print(f"   Title: {result['title']}")
        print(f"   Artist: {result['artist']}")
        
        if result.get('romanization'):
            print("\n🔤 Romanization available!")
            romaji_lines = result['romanization'].split('\n')[:3]
            print("   Preview:")
            for line in romaji_lines:
                if line.strip():
                    print(f"   {line}")
        else:
            print("\n⚠️  Romanization not available")
    else:
        print("❌ Not found")


def demo_direct_api():
    """Demo 6: Using provider APIs directly."""
    print("\n" + "="*60)
    print("DEMO 6: Direct Provider APIs")
    print("="*60)
    
    print("\n📌 Using LRCLIB API directly:")
    lrclib = LRCLIBFetcher()
    result = lrclib.get_best_match("Yesterday", "The Beatles")
    
    if result:
        print(f"   ✅ Title: {result.get('title')}")
        print(f"   Has Synced: {bool(result.get('synced_lyrics'))}")
    
    print("\n📌 Using Musixmatch API directly:")
    mxm = MusixmatchFetcher()
    result = mxm.get_best_match("Yesterday", "The Beatles")
    
    if result:
        print(f"   ✅ Title: {result.title}")
        print(f"   Rating: {result.rating}")
        print(f"   Has Subtitles: {result.has_subtitles}")


def main():
    """Run all demos."""
    print("\n" + "="*60)
    print("🎵 LyricFlow Multi-Provider Demo")
    print("="*60)
    print("\nThis demo showcases all features of the lyrics fetching system.")
    print("Press Ctrl+C to skip any demo.\n")
    
    demos = [
        ("LRCLIB (Free Provider)", demo_lrclib),
        ("Musixmatch Provider", demo_musixmatch),
        ("Factory Function", demo_factory),
        ("Fallback Strategy", demo_fallback),
        ("Romanization", demo_romanization),
        ("Direct APIs", demo_direct_api),
    ]
    
    for name, demo_func in demos:
        try:
            input(f"\n▶️  Press Enter to run: {name} (or Ctrl+C to skip)")
            demo_func()
        except KeyboardInterrupt:
            print(f"\n⏭️  Skipped: {name}")
            continue
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            continue
    
    print("\n" + "="*60)
    print("✨ Demo Complete!")
    print("="*60)
    print("\nGenerated files:")
    for file in Path(".").glob("demo_*.lrc"):
        print(f"  📄 {file}")
    
    print("\n📚 For more information:")
    print("  • docs/PROVIDERS_GUIDE.md - Provider comparison")
    print("  • docs/MUSIXMATCH_GUIDE.md - Musixmatch guide")
    print("  • MULTI_PROVIDER_COMPLETE.md - Implementation summary")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        raise
