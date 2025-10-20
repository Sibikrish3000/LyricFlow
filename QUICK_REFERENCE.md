# 🎯 Quick Reference - LyricFlow CLI

## Interactive Mode (No Title Required!)

```bash
# Launch empty TUI
lyricflow fetch -i

# Pre-fill title
lyricflow fetch -i -t "Yesterday"

# Pre-fill title and artist
lyricflow fetch -i -t "Yesterday" -a "The Beatles"

# With audio file (auto-fills from metadata)
lyricflow fetch -i --audio song.m4a

# With provider selection
lyricflow fetch -i -p musixmatch

# Everything combined
lyricflow fetch -i -t "Song" -a "Artist" -p musixmatch --audio song.m4a
```

## Non-Interactive Mode (Title Required)

```bash
# Basic fetch
lyricflow fetch -t "Yesterday" -a "The Beatles"

# With provider
lyricflow fetch -t "Song" -a "Artist" -p musixmatch

# Save to file
lyricflow fetch -t "Song" -a "Artist" -o lyrics.lrc

# Embed in audio
lyricflow fetch -t "Song" -a "Artist" --audio song.m4a --embed

# With romanization
lyricflow fetch -t "Song" -a "Artist" --romanization

# With translation (Musixmatch only)
lyricflow fetch -t "Song" -a "Artist" -p musixmatch --translation
```

## Providers

| Provider | Cost | API Key | Translations | Romanization |
|----------|------|---------|--------------|--------------|
| **LRCLIB** | Free | No | No | Via LyricFlow |
| **Musixmatch** | Free tier | Optional | Yes | Via LyricFlow |

```bash
# Default (LRCLIB)
lyricflow fetch -t "Song" -a "Artist"

# Musixmatch
lyricflow fetch -t "Song" -a "Artist" -p musixmatch
```

## Common Workflows

### 1. Search and Preview
```bash
# Interactive search
lyricflow fetch -i -t "Yesterday" -a "Beatles"
# → Search → Preview → Save/Embed manually in TUI
```

### 2. Quick Fetch and Save
```bash
lyricflow fetch -t "Yesterday" -a "Beatles" -o yesterday.lrc
```

### 3. Embed in Audio
```bash
lyricflow fetch -t "Song" -a "Artist" --audio song.m4a --embed
```

### 4. Batch Process with Audio Files
```bash
# For each audio file in directory
for file in *.m4a; do
    lyricflow fetch -i --audio "$file"
done
```

## Options Reference

```
-t, --title          Song title (required in non-interactive)
-a, --artist         Artist name (optional)
-l, --album          Album name (optional)
--audio PATH         Audio file for metadata/embedding
-o, --output PATH    Save lyrics to .lrc file
-p, --provider       lrclib (default) or musixmatch
--translation        Fetch translation (Musixmatch only)
--romanization       Romanize lyrics
--embed              Embed lyrics into audio file
-i, --interactive    Launch TUI
```

## Keyboard Shortcuts (TUI)

```
Tab              Navigate between fields
Enter            Search / Submit
Ctrl+S           Search
Ctrl+Q           Quit
Escape           Clear
↑/↓              Navigate results
Click            Select buttons/results
```

## Error Messages

### Title Required
```bash
$ lyricflow fetch -a "Artist"
❌ Error: --title is required in non-interactive mode
Tip: Use --interactive (-i) to launch TUI without title
```

**Fix:** Add `-i` flag or provide `--title`

### No Results
```bash
❌ No lyrics found
```

**Fix:** Try different spelling, provider, or add more details

### Provider Error
```bash
⚠️ Translation only available with Musixmatch
```

**Fix:** Add `-p musixmatch` flag

## Tips & Tricks

### Tip 1: Start with Interactive
```bash
# Don't know exact spelling? Use TUI!
lyricflow fetch -i
```

### Tip 2: Use Audio Files
```bash
# Let the tool read metadata for you
lyricflow fetch -i --audio song.m4a
```

### Tip 3: Try Both Providers
```bash
# LRCLIB first (free)
lyricflow fetch -t "Song" -a "Artist"

# If not found, try Musixmatch
lyricflow fetch -t "Song" -a "Artist" -p musixmatch
```

### Tip 4: Save Before Embedding
```bash
# Save .lrc first to preview
lyricflow fetch -t "Song" -a "Artist" -o test.lrc

# Then embed if happy
lyricflow fetch -t "Song" -a "Artist" --audio song.m4a --embed
```

## Quick Tests

```bash
# Test 1: Empty TUI
lyricflow fetch -i

# Test 2: Pre-filled TUI
lyricflow fetch -i -t "Yesterday" -a "Beatles"

# Test 3: LRCLIB
lyricflow fetch -t "Yesterday" -a "The Beatles"

# Test 4: Musixmatch
lyricflow fetch -t "Yesterday" -a "The Beatles" -p musixmatch

# Test 5: Error message
lyricflow fetch -a "Artist"
```

## Status Indicators (TUI)

```
🔍 Searching...        - Fetching lyrics
✅ Found match         - Lyrics retrieved
❌ No results found    - Nothing found
⚠️  Warning            - Partial success
```

## Exit Codes

```
0   Success
1   Error (with message)
```

---

**Quick Help:** `lyricflow fetch --help`  
**Full Docs:** See README.md, INTEGRATION_COMPLETE.md  
**Version:** 1.0.2
