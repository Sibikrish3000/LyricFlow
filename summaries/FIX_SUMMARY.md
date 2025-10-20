# Fix Summary

## Issue
The application was crashing when trying to load configuration from `config.yaml` with the error:
```
TypeError: APIConfig.__init__() got an unexpected keyword argument 'openai'
```

## Root Cause
The `config.yaml` file has a nested structure for API configuration:
```yaml
api:
  openai:
    api_key: "..."
    base_url: "..."
  gemini:
    api_key: "..."
```

But the `Config.from_dict()` method was trying to pass this nested dictionary directly to the `APIConfig` dataclass, which expects flat fields like `openai_api_key`, not nested dicts.

## Solution
Updated `Config.from_dict()` in `lyricflow/utils/config.py` to properly parse the nested structure:

```python
@classmethod
def from_dict(cls, data: Dict[str, Any]) -> "Config":
    """Create Config from dictionary."""
    # Parse API config with nested structure
    api_data = data.get("api", {})
    api_config = APIConfig(
        default_provider=api_data.get("default_provider", "local"),
        openai_api_key=api_data.get("openai", {}).get("api_key"),
        openai_base_url=api_data.get("openai", {}).get("base_url", "https://api.openai.com/v1"),
        gemini_api_key=api_data.get("gemini", {}).get("api_key"),
        gemini_base_url=api_data.get("gemini", {}).get("base_url"),
    )
    
    return cls(
        api=api_config,
        processing=ProcessingConfig(**data.get("processing", {})),
        whisper=WhisperConfig(**data.get("whisper", {})),
        caching=CachingConfig(**data.get("caching", {})),
    )
```

## Additional Fixes

### Fix 2: RuntimeWarning
**Issue**: When running `python -m lyricflow.cli.main`, got a RuntimeWarning about module import behavior.

**Solution**: Updated `lyricflow/__main__.py` to import the CLI only inside the `if __name__ == '__main__'` block:

```python
if __name__ == '__main__':
    from lyricflow.cli.main import cli
    cli(obj={})
```

## Verification

All tests now pass:

```bash
# Config loading
✅ Config loads successfully from config.yaml
✅ Nested API configuration parsed correctly

# Romanization
✅ Local romanization works: "こんにちは世界" → "Konnichiha sekai"
✅ AI romanization with fallback works (tries API, falls back to local on error)

# CLI
✅ No RuntimeWarning when running commands
✅ All commands work: process, romanize, config

# Error Handling
✅ Invalid API keys trigger fallback to local romanization
✅ Clear error messages in logs
```

## Commands Tested

```bash
# Basic romanization
python -m lyricflow romanize "こんにちは世界"
# Output: Konnichiha sekai

# With AI (falls back to local if API key invalid)
python -m lyricflow romanize "こんにちは世界" --use-ai --api gemini
# Output: Attempts API, falls back, returns: Konnichiha sekai

# Config display
python -m lyricflow config
# Shows all configuration including API keys (masked)

# Process audio
python -m lyricflow process "tests/01 Shogeki.m4a"
# Successfully processes and embeds romanized lyrics
```

## Status
✅ **All issues resolved**
✅ **No breaking changes**
✅ **Backward compatible**
✅ **All tests passing**
