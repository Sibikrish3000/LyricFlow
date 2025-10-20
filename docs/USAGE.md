# LyricFlow Usage Guide

## Installation

```bash
# Install core package
pip install -e .

# Or with all features
pip install -e ".[all]"
```

## Quick Start Examples

### 1. Process a Single Audio File

```bash
# Basic processing - will find .lrc file and embed romanized lyrics
python -m lyricflow process "tests/01 Shogeki.m4a"

# With AI romanization (requires API key)
python -m lyricflow process "song.mp3" --use-ai --api openai

# Process without embedding (just create _romaji.lrc file)
python -m lyricflow process "song.mp3" --no-embed
```

### 2. Process an Entire Music Directory

```bash
# Process all audio files recursively
python -m lyricflow process "/path/to/music" --recursive

# Process with overwrite (reprocess even if romanized lyrics exist)
python -m lyricflow process "/path/to/music" --overwrite

# Dry run to see what would be processed
python -m lyricflow process "/path/to/music" --dry-run
```

### 3. Romanize Text Directly

```bash
# Romanize text from command line
python -m lyricflow romanize "こんにちは世界"

# Romanize from file
python -m lyricflow romanize --file lyrics.txt

# Romanize with AI (OpenAI)
python -m lyricflow romanize "こんにちは" --use-ai --api openai

# Romanize with AI (Gemini)
python -m lyricflow romanize "こんにちは" --use-ai --api gemini
```

### 4. View Configuration

```bash
python -m lyricflow config
```

## Configuration

### Option 1: Configuration File

Create `config.yaml` in project root:

```yaml
api:
  default_provider: local  # or openai, gemini
  openai:
    api_key: "sk-..."
    base_url: "https://api.openai.com/v1"
  gemini:
    api_key: "..."

processing:
  language: auto
  skip_existing_lyrics: true
```

### Option 2: Environment Variables

```bash
# Set API keys
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export LYRICFLOW_API_PROVIDER="openai"
```

### Option 3: Custom Base URL (for Local LLMs)

```yaml
api:
  openai:
    api_key: "dummy"
    base_url: "http://localhost:1234/v1"
```

## API Server

### Start the FastAPI Server

```bash
# Using uvicorn directly
uvicorn lyricflow.api.server:app --reload --port 8000

# Or using Python
python -m lyricflow.api.server
```

### API Endpoints

- **POST /process** - Upload audio file for processing
  ```bash
  curl -X POST "http://localhost:8000/process" \
    -F "file=@song.mp3" \
    -F "use_ai=false"
  ```

- **GET /status/{task_id}** - Check processing status
  ```bash
  curl "http://localhost:8000/status/{task_id}"
  ```

- **POST /romanize** - Romanize text
  ```bash
  curl -X POST "http://localhost:8000/romanize" \
    -H "Content-Type: application/json" \
    -d '{"text":"こんにちは","language":"ja"}'
  ```

- **Interactive Docs**: http://localhost:8000/docs

## Python API Usage

### Basic Usage

```python
from pathlib import Path
from lyricflow import LyricsSync, Romanizer, AudioHandler

# Process an audio file
lyrics_sync = LyricsSync()
result = lyrics_sync.process_audio_file(
    Path("song.mp3"),
    use_ai=False,
    overwrite=False,
    no_embed=False
)
print(result)
```

### Romanize Text

```python
from lyricflow import Romanizer

romanizer = Romanizer()
result = romanizer.romanize("こんにちは世界", language="ja")
print(result)  # "Konnichiha sekai"
```

### Handle Audio Metadata

```python
from pathlib import Path
from lyricflow.core.audio_handler import AudioHandler, LyricType

# Read metadata
audio = AudioHandler(Path("song.mp3"))
metadata = audio.get_metadata()
print(f"Title: {metadata['title']}")
print(f"Artist: {metadata['artist']}")

# Check for existing lyrics
if audio.has_romanized_lyrics():
    print("Already has romanized lyrics")

# Embed lyrics
success = audio.embed_lyrics(
    "Romanized lyrics content...",
    lyric_type=LyricType.ROMANIZED
)
```

### Process Directory

```python
from pathlib import Path
from lyricflow import LyricsSync

lyrics_sync = LyricsSync()
results = lyrics_sync.process_directory(
    Path("/path/to/music"),
    recursive=True,
    use_ai=False,
    overwrite=False
)

for result in results:
    print(f"{result['file']}: {result['status']}")
```

## Advanced Features

### Custom Configuration

```python
from lyricflow.utils.config import Config, APIConfig, ProcessingConfig

config = Config()
config.api.default_provider = "openai"
config.api.openai_api_key = "sk-..."
config.processing.language = "ja"

# Save configuration
config.save(Path("custom_config.yaml"))

# Load configuration
config = Config.from_yaml(Path("custom_config.yaml"))
```

### AI Romanization

```python
from lyricflow import Romanizer

romanizer = Romanizer()

# Force AI romanization
result = romanizer.romanize(
    "こんにちは世界",
    language="ja",
    use_ai=True
)
```

## Workflow

LyricFlow follows this workflow when processing audio files:

1. **Check Embedded Romanized Lyrics**
   - If exists → Skip (unless `--overwrite`)

2. **Check Embedded Synced Lyrics**
   - If exists → Romanize → Embed → Save .lrc

3. **Search for Local .lrc File**
   - If exists → Romanize → Embed → Save _romaji.lrc

4. **No Lyrics Found**
   - Suggest using Whisper generation

## Supported Audio Formats

- MP3 (ID3v2 tags)
- M4A/MP4 (iTunes tags)
- FLAC (Vorbis comments)
- OGG Vorbis
- OPUS
- WMA

## Tag Types

- **USLT** (ID3) - Unsynced lyrics
- **SYLT** (ID3) - Synced lyrics
- **©lyr** (MP4) - Lyrics
- **TXXX:Romanized_Lyrics** (ID3) - Romanized lyrics
- **----:com.apple.iTunes:Romanized_Lyrics** (MP4) - Romanized lyrics

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Reinstall with all dependencies
pip install -e ".[all]"

# Or install specific features
pip install -e ".[api,openai]"
```

### API Key Issues

```bash
# Check if API key is set
python -m lyricflow config

# Set via environment
export OPENAI_API_KEY="sk-..."

# Or use config file
cp config.yaml.example config.yaml
# Edit config.yaml with your API keys
```

### Permission Errors

If you get permission errors when embedding lyrics:

- Ensure audio files are not read-only
- Check file permissions
- Try running with elevated privileges (Windows: Run as Administrator)

## Examples

### Example 1: Batch Process Music Library

```bash
# Process entire music library with progress
python -m lyricflow process "/path/to/Music" \
    --recursive \
    --api local \
    -v
```

### Example 2: Process with AI and Save LRC Only

```bash
# Use OpenAI for romanization but don't embed
python -m lyricflow process "song.mp3" \
    --use-ai \
    --api openai \
    --no-embed
```

### Example 3: Reprocess All Files

```bash
# Force reprocess even if romanized lyrics exist
python -m lyricflow process "/path/to/Music" \
    --recursive \
    --overwrite
```

## Tips

1. **Use Local Romanization First**: It's fast, free, and accurate for Japanese
2. **Use AI for Difficult Text**: Switch to AI for ambiguous or mixed-language text
3. **Batch Processing**: Process directories overnight for large libraries
4. **Backup First**: Always backup your music library before batch processing
5. **Check Config**: Run `lyricflow config` to verify settings before processing

## Getting Help

```bash
# General help
python -m lyricflow --help

# Command-specific help
python -m lyricflow process --help
python -m lyricflow romanize --help
```

## Further Reading

- [Full Documentation](README.md)
- [API Reference](https://lyricflow.readthedocs.io)
- [Issue Tracker](https://github.com/yourusername/lyricflow/issues)
