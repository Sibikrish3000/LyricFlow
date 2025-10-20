# Multi-Provider Lyrics Fetching

## Overview

LyricFlow supports **multiple lyrics providers** with a unified interface:

| Provider | Type | Synced | Unsynced | Translation | Free | Quality |
|----------|------|--------|----------|-------------|------|---------|
| **LRCLIB** | Free/Open | ✅ | ✅ | ❌ | ✅ | ⭐⭐⭐⭐ |
| **Musixmatch** | Commercial | ✅ | ✅ | ✅ | ⚠️ | ⭐⭐⭐⭐⭐ |

### Quick Comparison

**LRCLIB:**
- ✅ Completely free and open-source
- ✅ No API key required
- ✅ Good coverage for popular music
- ✅ Clean, simple API
- ❌ No translations
- ❌ Smaller database than Musixmatch

**Musixmatch:**
- ✅ Largest lyrics database
- ✅ High-quality synced lyrics
- ✅ Translations available
- ✅ High match accuracy
- ⚠️ Free tier with limitations
- ❌ Requires token (auto-fetched)

## Installation

```bash
# Basic fetch support (both providers)
pip install lyricflow[fetch]

# With TUI support
pip install lyricflow[tui]
```

## CLI Usage

### LRCLIB (Default, Free)

```bash
# Basic search (LRCLIB is default)
lyricflow fetch -t "Bohemian Rhapsody" -a "Queen"

# Explicit LRCLIB
lyricflow fetch -t "Song" -a "Artist" --provider lrclib

# Save to file
lyricflow fetch -t "Song" -a "Artist" -o output.lrc

# With romanization
lyricflow fetch -t "千本桜" -a "初音ミク" --romanization
```

### Musixmatch

```bash
# Use Musixmatch
lyricflow fetch -t "Song" -a "Artist" --provider musixmatch

# With translation (Musixmatch only)
lyricflow fetch -t "Song" -a "Artist" -p musixmatch --translation

# Everything
lyricflow fetch \
  -t "Song" -a "Artist" \
  --provider musixmatch \
  --translation \
  --romanization \
  --audio song.m4a \
  --embed
```

### Comparison Examples

```bash
# Try LRCLIB first (free)
lyricflow fetch -t "Yesterday" -a "Beatles" -p lrclib

# If not found, try Musixmatch
lyricflow fetch -t "Yesterday" -a "Beatles" -p musixmatch
```

## Python API

### Unified Interface

```python
from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher

# Use LRCLIB (free)
fetcher = UnifiedLyricsFetcher(provider="lrclib")
result = fetcher.fetch("Bohemian Rhapsody", "Queen")

if result:
    print(f"Found: {result['title']} by {result['artist']}")
    print(f"Type: {'Synced' if result['has_synced'] else 'Plain'}")
    print(f"Lyrics: {result['synced_lyrics'] or result['plain_lyrics']}")
```

### Provider-Specific APIs

#### LRCLIB

```python
from lyricflow.core.lrclib import LRCLIBFetcher
from pathlib import Path

fetcher = LRCLIBFetcher()

# Search
result = fetcher.search(
    title="Bohemian Rhapsody",
    artist="Queen",
    album="A Night at the Opera",
    duration=354  # Optional, improves accuracy
)

if result:
    # Save to file
    fetcher.save_lrc(result, Path("output.lrc"))
    
    print(f"Found: {result['title']}")
    print(f"Synced: {bool(result['synced_lyrics'])}")
```

#### Musixmatch

```python
from lyricflow.core.musixmatch import MusixmatchFetcher

fetcher = MusixmatchFetcher()

# Get best match
result = fetcher.get_best_match(
    title="Bohemian Rhapsody",
    artist="Queen"
)

if result:
    print(f"Match score: {result.match_score('Bohemian Rhapsody', 'Queen')}")
    print(f"Rating: {result.rating}")
```

### Factory Function

```python
from lyricflow.core.lyrics_provider import create_fetcher

# Auto-select free provider
fetcher = create_fetcher(prefer_free=True)  # Uses LRCLIB

# Specific provider
fetcher = create_fetcher(provider="musixmatch")
```

### Fallback Strategy

```python
from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher

def fetch_with_fallback(title, artist):
    """Try LRCLIB first, fallback to Musixmatch."""
    
    # Try free provider first
    fetcher = UnifiedLyricsFetcher(provider="lrclib")
    result = fetcher.fetch(title, artist)
    
    if result:
        print("✅ Found on LRCLIB (free)")
        return result
    
    # Fallback to Musixmatch
    print("⚠️  Not found on LRCLIB, trying Musixmatch...")
    fetcher = UnifiedLyricsFetcher(provider="musixmatch")
    result = fetcher.fetch(title, artist)
    
    if result:
        print("✅ Found on Musixmatch")
        return result
    
    print("❌ Not found on any provider")
    return None

# Usage
result = fetch_with_fallback("Song Title", "Artist Name")
```

## TUI Support

The TUI will support provider selection in a future update. Currently uses the default provider.

## FastAPI Endpoints

### Provider Selection

```bash
# Search on LRCLIB
curl -X POST "http://localhost:8000/fetch/search" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "provider": "lrclib"
  }'

# Search on Musixmatch
curl -X POST "http://localhost:8000/fetch/search" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "provider": "musixmatch",
    "fetch_translation": true
  }'
```

## Feature Comparison

### Data Quality

| Feature | LRCLIB | Musixmatch |
|---------|--------|------------|
| Popular Songs | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Niche/Indie | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Non-English | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Sync Accuracy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Database Size | Medium | Very Large |

### API Features

| Feature | LRCLIB | Musixmatch |
|---------|--------|------------|
| Synced Lyrics | ✅ | ✅ |
| Plain Lyrics | ✅ | ✅ |
| Translation | ❌ | ✅ |
| Search | ✅ | ✅ |
| Metadata | ✅ | ✅ |
| Rating | ❌ | ✅ |
| Duration Match | ✅ | ❌ |

### Cost & Limits

| Aspect | LRCLIB | Musixmatch |
|--------|--------|------------|
| Cost | Free | Free tier + Paid |
| API Key | ❌ Not needed | ⚠️ Auto-fetched |
| Rate Limit | Generous | Limited on free tier |
| Commercial Use | ✅ | ⚠️ Check terms |

## Best Practices

### When to Use LRCLIB

✅ **Use LRCLIB for:**
- Personal projects
- Popular Western music
- When you need 100% free solution
- Batch processing (no rate limits)
- Open-source projects

### When to Use Musixmatch

✅ **Use Musixmatch for:**
- Professional applications
- International music
- When you need translations
- When you need highest quality
- Maximum coverage needed

### Recommended Strategy

```python
# 1. Try LRCLIB first (free)
# 2. Fallback to Musixmatch if not found
# 3. Cache results to avoid repeated API calls

from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher
import json
from pathlib import Path

def smart_fetch(title, artist, cache_dir=None):
    """Smart fetching with caching and fallback."""
    
    # Check cache first
    if cache_dir:
        cache_file = Path(cache_dir) / f"{artist}_{title}.json"
        if cache_file.exists():
            print("📦 Using cached lyrics")
            return json.loads(cache_file.read_text())
    
    # Try LRCLIB (free)
    print("🔍 Trying LRCLIB...")
    fetcher = UnifiedLyricsFetcher(provider="lrclib")
    result = fetcher.fetch(title, artist)
    
    if result:
        print("✅ Found on LRCLIB")
        if cache_dir:
            cache_file.write_text(json.dumps(result))
        return result
    
    # Fallback to Musixmatch
    print("🔍 Trying Musixmatch...")
    fetcher = UnifiedLyricsFetcher(provider="musixmatch")
    result = fetcher.fetch(title, artist)
    
    if result:
        print("✅ Found on Musixmatch")
        if cache_dir:
            cache_file.write_text(json.dumps(result))
        return result
    
    return None
```

## Configuration

### Provider Selection in Config

```yaml
# ~/.lyricflow/config.yaml

lyrics_fetch:
  default_provider: lrclib  # or musixmatch
  fallback_enabled: true
  cache_results: true
  cache_ttl: 2592000  # 30 days
```

### Environment Variables

```bash
# Force specific provider
export LYRICFLOW_PROVIDER=lrclib

# Musixmatch token (optional, auto-fetched if not set)
export MUSIXMATCH_TOKEN=your_token_here
```

## Troubleshooting

### LRCLIB Issues

**"No results found"**
- LRCLIB has smaller database
- Try Musixmatch as fallback
- Check spelling
- Try without album name

**"Connection timeout"**
- Check internet connection
- LRCLIB API might be down
- Try again later

### Musixmatch Issues

**"Failed to get token"**
- Network issue
- Try again (tokens are cached)
- Check if API is accessible in your region

**"No lyrics found"**
- Song might not be in database
- Try LRCLIB as alternative
- Use interactive TUI to see all results

## Migration from Musixmatch-only

If you were using Musixmatch before:

```python
# Old code
from lyricflow.core.musixmatch import MusixmatchFetcher
fetcher = MusixmatchFetcher()
result = fetcher.get_best_match("Song", "Artist")

# New unified code (still works with Musixmatch)
from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher
fetcher = UnifiedLyricsFetcher(provider="musixmatch")
result = fetcher.fetch("Song", "Artist")

# Or use free alternative
fetcher = UnifiedLyricsFetcher(provider="lrclib")
result = fetcher.fetch("Song", "Artist")
```

## Future Providers

Planned for future releases:
- Genius
- AZLyrics  
- NetEase Music
- QQ Music
- Local LRC file database

## Credits

- **LRCLIB**: Free, open-source lyrics database
- **Musixmatch**: Commercial lyrics provider
- **LyricFlow**: Integration layer

## License

Each provider has its own terms of service. Please review:
- LRCLIB: Open-source, free use
- Musixmatch: Commercial, check their ToS

LyricFlow integration: MIT License
