# Quick Model Configuration Guide

## Overview
LyricFlow now supports configurable AI models for both OpenAI and Gemini APIs. You can set models in `config.yaml` or override with environment variables.

## Supported Models

### Gemini (Google AI)
- **gemini-2.0-flash-exp** (default) - Fast, accurate, recommended
- **gemini-2.5-pro** - Latest model with advanced reasoning
- **gemini-1.5-pro** - Stable production model
- **gemini-1.5-flash** - Fast and efficient

### OpenAI
- **gpt-3.5-turbo** (default) - Fast and cost-effective
- **gpt-4** - More accurate, slower, expensive
- **gpt-4-turbo** - Faster GPT-4
- **gpt-4o** - Optimized version

## Configuration Methods

### Method 1: Edit config.yaml (Persistent)

```yaml
api:
  gemini:
    api_key: "YOUR_KEY"
    model: "gemini-2.5-pro"  # Change this line
```

### Method 2: Environment Variable (Temporary Override)

**PowerShell:**
```powershell
# Set for current session
$env:GEMINI_MODEL = "gemini-2.5-pro"

# Or set for single command
$env:GEMINI_MODEL="gemini-2.5-pro"; python -m lyricflow romanize "text" --use-ai --api gemini
```

**Bash/Linux:**
```bash
export GEMINI_MODEL="gemini-2.5-pro"
python -m lyricflow romanize "text" --use-ai --api gemini
```

### Method 3: Inline for Single Command

**PowerShell:**
```powershell
$env:GEMINI_MODEL="gemini-2.5-pro"; python -m lyricflow process song.m4a --api gemini
```

## Check Current Configuration

```bash
python -m lyricflow config
```

Output shows active model:
```
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Setting         ┃ Value                     ┃
┃ Gemini Model    ┃ gemini-2.0-flash-exp      ┃
└─────────────────┴───────────────────────────┘
```

## Usage Examples

### Example 1: Using Default (config.yaml)
```bash
python -m lyricflow romanize "こんにちは" --use-ai --api gemini
# Uses: gemini-2.0-flash-exp (from config.yaml)
```

### Example 2: Override with Environment Variable
```powershell
$env:GEMINI_MODEL = "gemini-2.5-pro"
python -m lyricflow romanize "こんにちは" --use-ai --api gemini
# Uses: gemini-2.5-pro (from environment variable)
```

### Example 3: Process Audio File
```powershell
$env:GEMINI_MODEL = "gemini-2.5-pro"
python -m lyricflow process "song.m4a" --api gemini --overwrite
# Romanizes lyrics using gemini-2.5-pro
```

### Example 4: Testing Different Models
```powershell
# Test with fast model
$env:GEMINI_MODEL = "gemini-2.0-flash-exp"
python -m lyricflow romanize "テスト" --use-ai --api gemini

# Test with pro model
$env:GEMINI_MODEL = "gemini-2.5-pro"
python -m lyricflow romanize "テスト" --use-ai --api gemini
```

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `GEMINI_API_KEY` | Gemini API key | `AIzaSy...` |
| `GEMINI_MODEL` | Gemini model ID | `gemini-2.5-pro` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | OpenAI model ID | `gpt-4-turbo` |
| `LYRICFLOW_API_PROVIDER` | Default provider | `gemini`, `openai`, or `local` |

## Priority Order

1. **Environment Variables** ← Highest priority
2. **./config.yaml** (project directory)
3. **~/.lyricflow/config.yaml** (user home)
4. **Default values** ← Lowest priority

Environment variables always override config files!

## Troubleshooting

### Model Not Found (404 Error)
```
ERROR - AI romanization failed: 404 Client Error
```
**Solution:** The model doesn't exist or is deprecated. Try:
- `gemini-2.0-flash-exp`
- `gemini-2.5-pro`
- `gemini-1.5-pro`

### Which Model Should I Use?

| Use Case | Recommended Model | Reason |
|----------|------------------|---------|
| Daily use | `gemini-2.0-flash-exp` | Fast, accurate, free tier friendly |
| Best quality | `gemini-2.5-pro` | Most advanced reasoning |
| Production | `gemini-1.5-pro` | Stable, well-tested |
| Cost-sensitive | `gemini-2.0-flash-exp` | Efficient, good quality |

### Clearing Environment Variables

**PowerShell:**
```powershell
Remove-Item Env:GEMINI_MODEL
```

**Bash:**
```bash
unset GEMINI_MODEL
```

## Testing Your Configuration

```bash
# 1. Check loaded config
python -m lyricflow config

# 2. Test simple romanization
python -m lyricflow romanize "テスト" --use-ai --api gemini

# 3. Test with override
$env:GEMINI_MODEL="gemini-2.5-pro"; python -m lyricflow romanize "テスト" --use-ai --api gemini

# 4. Verify fallback works
$env:GEMINI_MODEL="invalid-model"; python -m lyricflow romanize "テスト" --use-ai --api gemini
# Should fall back to local romanization
```

## Advanced: Using google-genai SDK

The code snippet you provided uses the newer `google-genai` SDK. If you want to use it:

```python
# Install new SDK
pip install google-genai

# Your code works as-is with model configuration:
from google import genai
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = os.environ.get("GEMINI_MODEL", "gemini-2.5-pro")

# Use the model variable
client.models.generate_content_stream(model=model, ...)
```

Currently, LyricFlow uses the REST API directly for maximum compatibility and to avoid the SSL certificate issues we encountered.
