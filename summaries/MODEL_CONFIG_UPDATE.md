# Model Configuration Update

## Summary
Added support for configurable AI model IDs in `config.yaml` and environment variables, allowing users to easily switch between different OpenAI and Gemini models.

## Changes Made

### 1. Configuration Schema (`config.yaml`)
Added `model` field for both OpenAI and Gemini:

```yaml
api:
  default_provider: local
  openai:
    api_key: "YOUR_OPENAI_API_KEY_HERE"
    base_url: "https://api.openai.com/v1"
    model: "gpt-3.5-turbo"  # NEW: Configurable model
  gemini:
    api_key: "AIzaSy..."
    base_url: null
    model: "gemini-2.0-flash-exp"  # NEW: Configurable model
```

### 2. Configuration Classes (`lyricflow/utils/config.py`)

**APIConfig Dataclass:**
```python
@dataclass
class APIConfig:
    openai_model: str = "gpt-3.5-turbo"  # NEW
    gemini_model: str = "gemini-2.0-flash-exp"  # NEW
```

**Config Loading:**
- Loads model values from YAML
- Environment variables now **override** YAML values (priority order changed)
- Supported environment variables:
  - `OPENAI_MODEL` - Override OpenAI model
  - `GEMINI_MODEL` - Override Gemini model
  - `OPENAI_API_KEY` - Override OpenAI API key
  - `GEMINI_API_KEY` - Override Gemini API key
  - `LYRICFLOW_API_PROVIDER` - Override default provider

### 3. Romanizer (`lyricflow/core/romanizer.py`)

**AIRomanizer Constructor:**
```python
def __init__(
    self,
    provider: Literal["openai", "gemini"],
    api_key: str,
    base_url: Optional[str] = None,
    model: Optional[str] = None,  # NEW parameter
):
    if provider == "openai":
        self.model = model or "gpt-3.5-turbo"
    elif provider == "gemini":
        self.model = model or "gemini-2.0-flash-exp"
```

**API Calls:**
- OpenAI: Uses `self.model` in `chat.completions.create()`
- Gemini: Uses `self.model` in REST API URL dynamically

### 4. CLI Display (`lyricflow/cli/main.py`)

Updated `config` command to show model information:
```
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Setting         ┃ Value                     ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ OpenAI Model    │ gpt-3.5-turbo             │
│ Gemini Model    │ gemini-2.0-flash-exp      │
└─────────────────┴───────────────────────────┘
```

## Usage Examples

### Using config.yaml
```yaml
api:
  gemini:
    model: "gemini-2.5-pro"
```

```bash
python -m lyricflow romanize "こんにちは" --use-ai --api gemini
# Uses gemini-2.5-pro from config.yaml
```

### Using Environment Variables (Priority Override)
```powershell
# Override model for single command
$env:GEMINI_MODEL="gemini-2.5-pro"
python -m lyricflow romanize "ありがとう" --use-ai --api gemini

# Override OpenAI model
$env:OPENAI_MODEL="gpt-4-turbo"
python -m lyricflow romanize "世界" --use-ai --api openai
```

### Check Current Configuration
```bash
python -m lyricflow config
```

## Tested Models

### Gemini Models (Working)
- ✅ `gemini-2.0-flash-exp` (default, fast & accurate)
- ✅ `gemini-2.5-pro` (tested, working)
- ❌ `gemini-pro` (404 error - may be deprecated)

### OpenAI Models (Supported, not tested yet)
- `gpt-3.5-turbo` (default)
- `gpt-4`
- `gpt-4-turbo`
- `gpt-4o`

## Test Results

### Test 1: Config.yaml Default
```bash
Input:  こんにちは世界
Model:  gemini-2.0-flash-exp (from config.yaml)
Output: Konnichiwa sekai
Status: ✅ Success
```

### Test 2: Environment Variable Override
```bash
$env:GEMINI_MODEL="gemini-2.5-pro"
Input:  ありがとう
Model:  gemini-2.5-pro (from env var, overriding config.yaml)
Output: arigatō
Status: ✅ Success
```

### Test 3: Invalid Model Fallback
```bash
$env:GEMINI_MODEL="gemini-pro"
Input:  ありがとう
Model:  gemini-pro (from env var)
Error:  404 Client Error - model not found
Fallback: Local romanization (pykakasi + fugashi)
Output: Ariga tō
Status: ✅ Fallback working
```

## Configuration Priority Order

1. **Environment Variables** (Highest priority)
   - `GEMINI_MODEL`, `OPENAI_MODEL`, etc.
   
2. **Project config.yaml** (./config.yaml)
   - Located in current directory
   
3. **User config.yaml** (~/.lyricflow/config.yaml)
   - Located in user home directory
   
4. **Default Values** (Lowest priority)
   - Built-in defaults in APIConfig dataclass

## Benefits

1. **Flexibility**: Easy to switch models without code changes
2. **Testing**: Test different models with environment variables
3. **Cost Control**: Use cheaper models for testing, expensive for production
4. **Future-Proof**: Easy to adopt new models as they're released
5. **Per-Command Override**: Use different models for different tasks
6. **Automatic Fallback**: Falls back to local romanization on API errors

## Code Example from Google AI Studio

Your provided example uses the new `google-genai` SDK (different from `google-generativeai`):

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
model = "gemini-2.5-pro"  # Configurable!

for chunk in client.models.generate_content_stream(
    model=model,
    contents=contents,
    config=generate_content_config,
):
    print(chunk.text, end="")
```

**Note**: We're currently using the REST API directly, which is more compatible. If you want to use the new `google-genai` SDK instead, we can update the implementation.

## Next Steps

1. ✅ Model configuration working
2. ⏳ Optional: Switch to `google-genai` SDK if preferred
3. ⏳ Add model validation/listing
4. ⏳ Add cost estimation per model
5. ⏳ Document recommended models for different use cases
6. ⏳ Add streaming support for long texts

## Related Files
- `config.yaml` - User configuration
- `lyricflow/utils/config.py` - Configuration management
- `lyricflow/core/romanizer.py` - Model usage
- `lyricflow/cli/main.py` - CLI display
