# Musixmatch Lyrics Fetcher - User Guide

## Overview

LyricFlow now includes a powerful Musixmatch integration that can automatically download synced/unsynced lyrics with **three different interfaces**:

1. **CLI** - Fast, automatic best-match selection
2. **TUI (Textual)** - Interactive preview and manual selection
3. **FastAPI** - RESTful API for web integration

## Features

- ✅ **Synced Lyrics** (LRC format with timestamps)
- ✅ **Unsynced Lyrics** (Plain text)
- ✅ **Translation Support** (Musixmatch translations)
- ✅ **Romanization** (Using LyricFlow's local/AI romanizer)
- ✅ **Smart Matching** (Automatic best-match algorithm)
- ✅ **Embedding** (Direct embedding into audio files)
- ✅ **Preview** (Interactive TUI for selection)

## Installation

```bash
# Install with fetch support (requests library)
pip install lyricflow[fetch]

# Install with TUI support (interactive mode)
pip install lyricflow[tui]

# Install with everything
pip install lyricflow[all]
```

## Usage

### 1. CLI Mode - Fast & Automatic

**Basic search (shows preview):**
```bash
lyricflow fetch -t "Bohemian Rhapsody" -a "Queen"
```

**Save to LRC file:**
```bash
lyricflow fetch -t "Song Title" -a "Artist Name" -o output.lrc
```

**Fetch and embed to audio file:**
```bash
lyricflow fetch -t "Song Title" -a "Artist" --audio song.m4a --embed
```

**With romanization:**
```bash
lyricflow fetch -t "こんにちは" -a "日本アーティスト" --romanization -o output.lrc
```

**With translation:**
```bash
lyricflow fetch -t "Song Title" -a "Artist" --translation -o output.lrc
```

**Full example:**
```bash
lyricflow fetch \
  --title "Bohemian Rhapsody" \
  --artist "Queen" \
  --album "A Night at the Opera" \
  --audio "song.m4a" \
  --output "custom.lrc" \
  --romanization \
  --translation \
  --embed
```

### 2. TUI Mode - Interactive Selection

**Launch interactive TUI:**
```bash
lyricflow fetch -t "Song Title" -a "Artist" --interactive
```

**TUI with audio file (auto-fills metadata):**
```bash
lyricflow fetch --audio song.m4a --interactive
```

**TUI Features:**
- 📋 Search multiple results
- 👁️ Preview lyrics before selection
- ⚡ Real-time search
- 💾 Save to LRC file
- 📝 Embed directly to audio
- 🌍 Fetch translations
- 🔤 Generate romanization

**TUI Controls:**
- `Tab` / `Shift+Tab` - Navigate fields
- `Enter` - Search / Select
- `Ctrl+S` - Search
- `Ctrl+Q` - Quit
- `Escape` - Clear
- Mouse clicks work too!

**TUI Screenshot Flow:**
```
┌─────────────────────────────────────────────────┐
│ 🎵 LyricFlow - Musixmatch Lyrics Searcher      │
├─────────────────────────────────────────────────┤
│ Title:  [Bohemian Rhapsody            ]        │
│ Artist: [Queen                         ]        │
│ Album:  [A Night at the Opera          ]        │
│                                                 │
│ [ ] Fetch Translation  [ ] Fetch Romanization  │
│ [Search]                                        │
│                                                 │
│ ✅ Found 3 results                              │
├─────────────────────────────────────────────────┤
│ Results Table:                                  │
│ > Bohemian Rhapsody | Queen | A Night... | ... │
│   Bohemian Rhapsody | Queen | Greatest...| ... │
├─────────────────────────────────────────────────┤
│ Lyrics Preview:                                 │
│ [00:00.50]Is this the real life?               │
│ [00:04.25]Is this just fantasy?                │
│ ...                                             │
├─────────────────────────────────────────────────┤
│ [Save LRC] [Embed to Audio] [Cancel]           │
└─────────────────────────────────────────────────┘
```

### 3. FastAPI - Web Integration

**Start the server:**
```bash
uvicorn lyricflow.api.server:app --reload
```

**Search for lyrics:**
```bash
curl -X POST "http://localhost:8000/fetch/search" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "fetch_romanization": true
  }'
```

**Response:**
```json
{
  "query": {
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "album": ""
  },
  "results_count": 3,
  "results": [
    {
      "track_id": 12345,
      "title": "Bohemian Rhapsody",
      "artist": "Queen",
      "album": "A Night at the Opera",
      "duration": 354,
      "has_lyrics": true,
      "has_subtitles": true,
      "rating": 95,
      "match_score": 0.98,
      "synced_lyrics": "[00:00.50]Is this the real life?\\n[00:04.25]Is this just fantasy?...",
      "romanization": "..."
    }
  ]
}
```

**Get lyrics by track ID:**
```bash
curl "http://localhost:8000/fetch/12345?synced=true&romanization=true"
```

**API Documentation:**
Visit `http://localhost:8000/docs` for interactive Swagger UI

## Features in Detail

### Smart Matching Algorithm

The CLI mode automatically selects the best match using:

1. **Title Match** (50% weight)
   - Exact match: +50%
   - Partial match: +30%

2. **Artist Match** (30% weight)
   - Exact match: +30%
   - Partial match: +15%

3. **Synced Lyrics Bonus** (10% weight)
   - Has synced lyrics: +10%

4. **Rating Bonus** (10% weight)
   - Based on Musixmatch rating (0-100)

**Example:**
```bash
$ lyricflow fetch -t "Bohemian" -a "Queen"
✅ Best match: Bohemian Rhapsody - Queen (score: 0.95)
```

### Synced vs Unsynced Lyrics

**Synced Lyrics (LRC Format):**
```lrc
[ti:Bohemian Rhapsody]
[ar:Queen]
[al:A Night at the Opera]

[00:00.50]Is this the real life?
[00:04.25]Is this just fantasy?
[00:08.00]Caught in a landslide
```

**Unsynced Lyrics:**
```
Is this the real life?
Is this just fantasy?
Caught in a landslide
No escape from reality
```

**Priority:** CLI always prefers synced lyrics when available.

### Romanization

**How it works:**
1. Fetches original lyrics from Musixmatch
2. Uses LyricFlow's romanizer (local or AI)
3. Saves separate `_romaji.lrc` file

**Example:**
```bash
lyricflow fetch -t "こんにちは" -a "アーティスト" --romanization -o song.lrc
```

**Output:**
- `song.lrc` - Original lyrics with timestamps
- `song_romaji.lrc` - Romanized lyrics with timestamps

### Translation

**Note:** Musixmatch provides translations for some songs.

**Example:**
```bash
lyricflow fetch -t "Song" -a "Artist" --translation
```

**Output:** Translation will be included in the API response or shown in TUI.

### Embedding to Audio Files

**Supported formats:**
- MP3 (.mp3)
- M4A (.m4a)
- FLAC (.flac)
- OGG (.ogg)

**Example:**
```bash
# Fetch and embed in one command
lyricflow fetch -t "Song" -a "Artist" --audio song.m4a --embed

# Or use TUI for interactive selection
lyricflow fetch --audio song.m4a --interactive
# Then click "Embed to Audio" button
```

**What gets embedded:**
- Synced lyrics → SYLT tag (time-synced lyrics)
- Unsynced lyrics → USLT tag (unsynced lyrics text)
- Metadata preserved

## Advanced Usage

### Batch Processing with CLI

**Process multiple audio files:**
```bash
#!/bin/bash
for file in *.m4a; do
    echo "Processing: $file"
    
    # Extract filename without extension
    name="${file%.*}"
    
    # Auto-fetch lyrics (will use audio metadata)
    lyricflow fetch --audio "$file" --embed
done
```

### Custom Python Script

```python
from pathlib import Path
from lyricflow.core.musixmatch import MusixmatchFetcher

# Initialize fetcher
fetcher = MusixmatchFetcher()

# Search for lyrics
results = fetcher.search(
    title="Bohemian Rhapsody",
    artist="Queen",
    fetch_lyrics=True,
    fetch_romanization=True
)

# Get best match
best = fetcher.get_best_match("Bohemian Rhapsody", "Queen")

if best:
    print(f"Found: {best.title} by {best.artist}")
    
    # Save to file
    output = Path("output.lrc")
    fetcher.save_lrc(best, output)
    print(f"Saved to {output}")
```

### FastAPI Integration

**Webhook example:**
```python
import requests

# Your Flask/Django/FastAPI server
@app.post("/fetch-lyrics")
async def fetch_lyrics(song_data: dict):
    # Call LyricFlow API
    response = requests.post(
        "http://localhost:8000/fetch/search",
        json={
            "title": song_data["title"],
            "artist": song_data["artist"],
            "fetch_romanization": True
        }
    )
    
    results = response.json()
    
    # Get best match
    if results["results"]:
        best = results["results"][0]
        return best
    
    return {"error": "No lyrics found"}
```

## Configuration

**Environment Variables:**
```bash
# Optional: Configure romanization
export GEMINI_API_KEY="your-key"
export GEMINI_MODEL="gemini-2.5-pro"

# Or OpenAI
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4-turbo"
```

**Config file (`~/.lyricflow/config.yaml`):**
```yaml
api:
  default_provider: gemini  # or openai, local
  gemini:
    api_key: "your-key"
    model: "gemini-2.5-pro"
  openai:
    api_key: "your-key"
    model: "gpt-4-turbo"

processing:
  language: auto
  skip_existing_lyrics: true
```

## Troubleshooting

### "requests library not installed"
```bash
pip install lyricflow[fetch]
# or
pip install requests
```

### "textual library not installed"
```bash
pip install lyricflow[tui]
# or
pip install textual
```

### "No lyrics found"
**Possible reasons:**
1. Song not in Musixmatch database
2. Typo in title/artist name
3. Network connection issues

**Solutions:**
- Try different spelling
- Try artist-only search
- Use interactive TUI to see all results
- Check internet connection

### "Failed to get valid token"
**Reason:** Musixmatch API token acquisition failed

**Solution:**
- Check internet connection
- Try again (tokens are cached)
- Check if Musixmatch API is accessible in your region

### TUI crashes or looks weird
**Solutions:**
- Update terminal (Windows Terminal, iTerm2, etc.)
- Update textual: `pip install -U textual`
- Check terminal size (minimum 80x24 recommended)

## Examples

### Example 1: Basic Fetch
```bash
$ lyricflow fetch -t "Yesterday" -a "The Beatles"

🔍 Searching for: Yesterday by The Beatles
✅ Found match:
  Title:    Yesterday
  Artist:   The Beatles
  Album:    Help!
  Duration: 2:05
  Rating:   98
  Type:     Synced (LRC)

📄 Lyrics Preview:
  [00:00.50]Yesterday
  [00:03.25]All my troubles seemed so far away
  ...
```

### Example 2: Interactive TUI
```bash
$ lyricflow fetch -t "Imagine" --interactive

# TUI opens with search results
# Click on preferred version
# Preview lyrics in real-time
# Click "Save LRC" or "Embed to Audio"
```

### Example 3: Automatic Processing
```bash
$ lyricflow fetch --audio "song.m4a" --embed

🔍 Searching for: Song Title by Artist Name (from metadata)
✅ Found match: Song Title - Artist Name
📝 Embedding lyrics to audio file...
✅ Embedded lyrics to: song.m4a
✨ Done!
```

### Example 4: Japanese Song with Romanization
```bash
$ lyricflow fetch \
  -t "千本桜" \
  -a "初音ミク" \
  --romanization \
  -o senbonzakura.lrc

✅ Saved lyrics to: senbonzakura.lrc
✅ Saved romanization to: senbonzakura_romaji.lrc
```

## API Reference

### CLI Commands

```
lyricflow fetch [OPTIONS]

Options:
  -t, --title TEXT          Song title [required]
  -a, --artist TEXT         Artist name
  -l, --album TEXT          Album name
  --audio PATH              Audio file to embed lyrics
  -o, --output PATH         Output LRC file path
  --translation             Fetch translation
  --romanization            Fetch romanization
  --embed                   Embed lyrics to audio file
  -i, --interactive         Launch TUI for interactive selection
  -v, --verbose             Enable verbose logging
  --help                    Show this message and exit
```

### Python API

See `lyricflow/core/musixmatch.py` for full API documentation.

**Key classes:**
- `MusixmatchAPI` - Low-level API client
- `MusixmatchFetcher` - High-level fetcher
- `LyricResult` - Result container

## Credits

**Original Musixmatch Script:** ohyeah & TT  
**Python Integration:** LyricFlow Contributors  
**TUI Framework:** Textual by Textualize  

## License

MIT License - See LICENSE file for details
