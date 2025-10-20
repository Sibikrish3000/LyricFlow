# 🎵 Musixmatch Integration - Quick Start

## What's New

LyricFlow now includes **Musixmatch lyrics fetching** with three interfaces:

- **CLI** - Fast automatic downloads
- **TUI** - Interactive visual selection  
- **API** - REST endpoints for web apps

## Installation

```bash
# Basic fetch support
pip install lyricflow[fetch]

# With interactive TUI
pip install lyricflow[tui]

# Everything
pip install lyricflow[all]
```

## Quick Examples

### 1. CLI - Fast & Automatic

```bash
# Search and preview
lyricflow fetch -t "Bohemian Rhapsody" -a "Queen"

# Save to LRC file
lyricflow fetch -t "Song" -a "Artist" -o output.lrc

# Fetch and embed to audio
lyricflow fetch -t "Song" -a "Artist" --audio song.m4a --embed

# With romanization
lyricflow fetch -t "こんにちは" -a "Artist" --romanization
```

### 2. TUI - Interactive Selection

```bash
# Launch interactive interface
lyricflow fetch -t "Song" -a "Artist" --interactive

# Auto-fill from audio file metadata
lyricflow fetch --audio song.m4a --interactive
```

**TUI Preview:**
```
┌────────────────────────────────────────┐
│ 🎵 LyricFlow - Lyrics Searcher        │
├────────────────────────────────────────┤
│ Title:  [Song Title           ]       │
│ Artist: [Artist Name          ]       │
│ [Search]                               │
│                                        │
│ Results: (Select one)                  │
│ > Song Title - Artist [3:45] (Synced) │
│   Song Title - Artist [3:44] (Lyrics) │
│                                        │
│ Preview:                               │
│ [00:00.50]First line...               │
│ [00:03.25]Second line...              │
│                                        │
│ [Save LRC] [Embed] [Cancel]           │
└────────────────────────────────────────┘
```

### 3. FastAPI - Web Integration

```bash
# Start server
uvicorn lyricflow.api.server:app

# Search
curl -X POST "http://localhost:8000/fetch/search" \
  -H "Content-Type: application/json" \
  -d '{"title": "Song", "artist": "Artist"}'
```

## Features

✅ **Synced Lyrics** - LRC format with timestamps  
✅ **Unsynced Lyrics** - Plain text format  
✅ **Translations** - Musixmatch translations  
✅ **Romanization** - Using LyricFlow's romanizer  
✅ **Smart Matching** - Automatic best-match selection  
✅ **Preview** - See all results before choosing  
✅ **Embedding** - Direct audio file embedding  

## Workflow Examples

### Scenario 1: Quick Download
```bash
# One command to fetch and save
lyricflow fetch -t "Yesterday" -a "Beatles" -o yesterday.lrc
```

### Scenario 2: Careful Selection
```bash
# Use TUI to preview all matches
lyricflow fetch -t "Yesterday" --interactive
# Browse results → Select best match → Save/Embed
```

### Scenario 3: Batch Processing
```bash
# Process entire music library
for file in *.m4a; do
  lyricflow fetch --audio "$file" --embed
done
```

### Scenario 4: Japanese Music
```bash
# Fetch with romanization
lyricflow fetch \
  -t "千本桜" \
  -a "初音ミク" \
  --romanization \
  --audio song.m4a \
  --embed

# Creates:
# - song.lrc (original Japanese)
# - song_romaji.lrc (romanized)
# - Embedded in song.m4a
```

## Smart Matching

CLI automatically selects best match based on:
- Title similarity (50%)
- Artist similarity (30%)
- Has synced lyrics bonus (10%)
- Rating score (10%)

**Example:**
```bash
$ lyricflow fetch -t "bohemian" -a "queen"
✅ Best match: Bohemian Rhapsody - Queen (score: 0.95)
```

## Configuration

Optional romanization with AI:

```bash
# Use Gemini
export GEMINI_API_KEY="your-key"

# Use OpenAI
export OPENAI_API_KEY="your-key"
```

Or local romanization (no API key needed):
- Japanese: pykakasi + fugashi
- Automatic fallback if API unavailable

## Troubleshooting

**"No lyrics found"**
- Try interactive TUI to see all results
- Check spelling
- Try different artist name variants

**"requests not installed"**
```bash
pip install lyricflow[fetch]
```

**"textual not installed"** (for TUI)
```bash
pip install lyricflow[tui]
```

## Full Documentation

See [`docs/MUSIXMATCH_GUIDE.md`](docs/MUSIXMATCH_GUIDE.md) for:
- Complete feature documentation
- API reference
- Advanced usage patterns
- Python API examples
- Troubleshooting guide

## Credits

- **Original Script:** ohyeah & TT
- **Integration:** LyricFlow Contributors
- **TUI Framework:** Textual

## Quick Links

- [Musixmatch Guide](docs/MUSIXMATCH_GUIDE.md) - Complete documentation
- [API Docs](http://localhost:8000/docs) - FastAPI interactive docs
- [GitHub Issues](https://github.com/yourusername/lyricflow/issues) - Report bugs

---

**Status:** ✅ Production Ready  
**Version:** 0.2.0  
**License:** MIT
