# 🎨 Enhancement: TUI Pre-filling & Optional Title

## Changes Made

### 1. ✅ TUI Pre-filling Support

**What:** The TUI now accepts initial values for title, artist, and album fields.

**Files Modified:**
- `lyricflow/tui/__init__.py`

**Changes:**

#### SearchScreen Constructor
```python
# BEFORE:
def __init__(self, audio_file: Optional[Path] = None, provider: str = "lrclib"):
    # Only read from audio file metadata
    
# AFTER:
def __init__(
    self,
    audio_file: Optional[Path] = None,
    provider: str = "lrclib",
    initial_title: str = "",      # ✨ NEW
    initial_artist: str = "",     # ✨ NEW
    initial_album: str = ""       # ✨ NEW
):
    # Accept initial values from parameters
    # Fall back to audio file metadata if not provided
```

#### LyricFlowTUI Class
```python
# BEFORE:
def __init__(self, audio_file: Optional[Path] = None, provider: str = "lrclib"):

# AFTER:
def __init__(
    self,
    audio_file: Optional[Path] = None,
    provider: str = "lrclib",
    initial_title: str = "",      # ✨ NEW
    initial_artist: str = "",     # ✨ NEW
    initial_album: str = ""       # ✨ NEW
):
```

#### launch_tui Function
```python
# BEFORE:
def launch_tui(audio_file: Optional[Path] = None, provider: str = "lrclib"):

# AFTER:
def launch_tui(
    audio_file: Optional[Path] = None,
    provider: str = "lrclib",
    initial_title: str = "",      # ✨ NEW
    initial_artist: str = "",     # ✨ NEW
    initial_album: str = ""       # ✨ NEW
):
```

### 2. ✅ Optional Title in CLI

**What:** Title is no longer required when using `--interactive` mode.

**Files Modified:**
- `lyricflow/cli/main.py`

**Changes:**

```python
# BEFORE:
@click.option('--title', '-t', required=True, help='Song title')

# AFTER:
@click.option('--title', '-t', help='Song title')  # ✨ No longer required

# Added validation in function:
if not title and not interactive:
    console.print("[red]❌ Error: --title is required in non-interactive mode[/red]")
    sys.exit(1)
```

### 3. ✅ CLI Passes Values to TUI

**What:** CLI now passes title, artist, and album to TUI for pre-filling.

```python
# BEFORE:
if interactive:
    launch_tui(audio_path, provider=provider)

# AFTER:
if interactive:
    launch_tui(
        audio_file=audio_path,
        provider=provider,
        initial_title=title or "",      # ✨ Pass through
        initial_artist=artist or "",    # ✨ Pass through
        initial_album=album or ""       # ✨ Pass through
    )
```

---

## Usage Examples

### 1. Empty TUI
```bash
# Launch TUI with empty fields
lyricflow fetch --interactive
lyricflow fetch -i
```

### 2. Pre-filled TUI
```bash
# Pre-fill title and artist
lyricflow fetch -i -t "Yesterday" -a "The Beatles"

# Pre-fill with album
lyricflow fetch -i -t "Song" -a "Artist" -l "Album"

# Pre-fill with specific provider
lyricflow fetch -i -t "Song" -a "Artist" -p musixmatch
```

### 3. With Audio File
```bash
# Launch TUI with audio file (reads metadata automatically)
lyricflow fetch -i --audio song.m4a

# Pre-fill title but use audio file for album
lyricflow fetch -i -t "Custom Title" --audio song.m4a
```

### 4. Non-Interactive (Title Required)
```bash
# This works (title provided)
lyricflow fetch -t "Song" -a "Artist"

# This fails with clear error message
lyricflow fetch -a "Artist"
# Error: --title is required in non-interactive mode
# Tip: Use --interactive (-i) to launch TUI without title
```

---

## Priority Logic

The TUI fields are filled with this priority:

1. **CLI parameters** (highest priority)
   - `--title`, `--artist`, `--album`

2. **Audio file metadata** (if file provided and no CLI values)
   - Read from audio file tags

3. **Empty** (default)
   - User enters values manually

**Example:**
```bash
# Title from CLI, Artist from audio file
lyricflow fetch -i -t "Custom Title" --audio song.m4a
# Result: Title="Custom Title", Artist=(from file), Album=(from file)

# Everything from audio file
lyricflow fetch -i --audio song.m4a
# Result: All fields from audio file metadata
```

---

## Benefits

### ✅ More Flexible
- Can launch TUI without knowing song details
- Can launch TUI with audio file only
- Can partially pre-fill fields

### ✅ Better UX
- No more "title is required" errors when using `-i`
- Pre-filled fields save typing
- Audio file metadata auto-detection still works

### ✅ More Intuitive
```bash
# OLD (confusing):
lyricflow fetch -i                 # ❌ Error: title required
lyricflow fetch -i --audio song.m4a  # ❌ Error: title required

# NEW (intuitive):
lyricflow fetch -i                 # ✅ Works! Empty TUI
lyricflow fetch -i --audio song.m4a  # ✅ Works! Pre-filled from audio
```

---

## Testing

### Manual Test
```bash
# Test 1: Empty TUI
lyricflow fetch -i

# Test 2: Pre-filled
lyricflow fetch -i -t "Yesterday" -a "Beatles"

# Test 3: With audio file
lyricflow fetch -i --audio tests/01\ Shogeki.m4a

# Test 4: Partial pre-fill
lyricflow fetch -i -t "Yesterday"

# Test 5: Error message (no title in non-interactive)
lyricflow fetch -a "Artist"
```

### Automated Test
```bash
python test_prefill.py
```

---

## Breaking Changes

### ⚠️ None!

This is fully backward compatible:
- Old commands still work
- API stays the same for programmatic use
- Only adds new optional parameters

---

## Files Modified

1. **`lyricflow/tui/__init__.py`**
   - Added `initial_title`, `initial_artist`, `initial_album` parameters
   - Updated `SearchScreen`, `LyricFlowTUI`, and `launch_tui`
   - ~40 lines changed

2. **`lyricflow/cli/main.py`**
   - Removed `required=True` from `--title` option
   - Added validation for non-interactive mode
   - Pass initial values to TUI
   - ~30 lines changed

3. **`test_prefill.py`**
   - New test script for pre-filling functionality
   - ~100 lines

---

## Status: ✅ COMPLETE

Both issues resolved:
1. ✅ TUI now accepts and uses pre-filled values
2. ✅ Title is optional when using `--interactive`
3. ✅ Clear error message when title missing in non-interactive mode
4. ✅ Backward compatible with existing commands

**Version:** 1.0.2  
**Date:** October 19, 2025
