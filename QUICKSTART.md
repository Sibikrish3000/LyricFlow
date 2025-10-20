# 🚀 LyricFlow Quick Start Guide

**Get lyrics in 30 seconds!**

---

## ⚡ Installation

```bash
# Install with all features
pip install -e ".[all]"

# Or install specific features
pip install -e ".[fetch]"      # CLI fetch only
pip install -e ".[tui]"         # CLI + TUI
```

---

## 🎯 Quick Commands

### Fetch Lyrics (CLI)
```bash
# Basic fetch (uses free LRCLIB)
lyricflow fetch -t "Yesterday" -a "The Beatles"

# Launch interactive TUI
lyricflow fetch --interactive

# Use Musixmatch (requires API key)
lyricflow fetch -t "Song" -a "Artist" --provider musixmatch

# With romanization
lyricflow fetch -t "Song" -a "Artist" --romanization

# Save to file
lyricflow fetch -t "Song" -a "Artist" -o song.lrc

# Embed in audio file
lyricflow fetch -t "Song" -a "Artist" --embed audio.m4a
```

### Test Everything
```bash
# Run all tests
python test_tui.py

# Run demos
python demo_providers.py

# Test specific provider
lyricflow fetch -t "Yesterday" -a "Beatles" --provider lrclib
```

---

## 🎨 TUI Usage

```bash
# Launch TUI
lyricflow fetch -i
# or
lyricflow fetch --interactive

# Inside TUI:
# 1. Select provider (LRCLIB is default, free)
# 2. Enter song details
# 3. Press Tab to navigate, Enter to search
# 4. Preview lyrics in bottom panel
# 5. Click "Save LRC" or "Embed in Audio"
# 6. Press Ctrl+C to exit
```

---

## 🔑 Configuration

### LRCLIB (Default - No Setup Required!)
✅ Works out of the box  
✅ No API key needed  
✅ Free forever  

### Musixmatch (Optional)
```bash
# Get API key from: https://developer.musixmatch.com/
export MUSIXMATCH_API_KEY="your_key_here"

# Or add to .env file
echo "MUSIXMATCH_API_KEY=your_key_here" >> .env
```

---

## 📖 Provider Comparison

| | LRCLIB | Musixmatch |
|---|---|---|
| Cost | ✅ **FREE** | ⚠️ API Key |
| Setup | ❌ None | ✅ Required |
| Synced Lyrics | ✅ Yes | ✅ Yes |
| Translations | ❌ No | ✅ Yes |
| Database | Medium | Large |

**Recommendation:** Use LRCLIB by default, Musixmatch for translations.

---

## 🧪 Test It Now

```bash
# Test 1: Fetch from LRCLIB
lyricflow fetch -t "Yesterday" -a "The Beatles"

# Test 2: Launch TUI
lyricflow fetch -i

# Test 3: Run test suite
python test_tui.py
```

---

## 📚 Learn More

- **Full Guide:** `INTEGRATION_COMPLETE.md`
- **Providers:** `docs/PROVIDERS_GUIDE.md`
- **Musixmatch:** `docs/MUSIXMATCH_GUIDE.md`
- **Demo Script:** `demo_providers.py`

---

## 🐛 Troubleshooting

**No results found?**
```bash
# Try different search terms
lyricflow fetch -t "Song Title" -a "Artist"

# Or try other provider
lyricflow fetch -t "Song Title" -a "Artist" --provider musixmatch
```

**Import errors?**
```bash
# Install dependencies
pip install -e ".[all]"

# Test imports
python -c "from lyricflow.tui import launch_tui; print('OK')"
```

**TUI not working?**
```bash
# Install textual
pip install textual

# Test TUI
python test_tui.py
```

---

## ✅ You're Ready!

**Three ways to use LyricFlow:**

1. **CLI:** `lyricflow fetch -t "Song" -a "Artist"`
2. **TUI:** `lyricflow fetch --interactive`
3. **API:** `uvicorn lyricflow.api.server:app`

**Start with:** `lyricflow fetch -t "Yesterday" -a "The Beatles"`

🎵 **Happy lyric hunting!**
