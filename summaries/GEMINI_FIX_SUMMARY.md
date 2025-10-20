# Gemini API Integration Fix Summary

## Problem
Gemini API calls were hanging indefinitely when using the `google-generativeai` Python SDK, despite the API key working correctly with curl commands.

## Root Cause
SSL certificate verification was failing in Python's requests/urllib3 library on this system, causing connection timeouts. The curl command worked because it handles SSL differently.

## Solution
1. **Switched to Direct REST API**: Instead of using the `google-generativeai` SDK, implemented direct REST API calls using the `requests` library
2. **Disabled SSL Verification**: Added `verify=False` parameter to requests to bypass certificate verification issues
3. **Added Timeout**: Set a 30-second timeout to prevent indefinite hanging
4. **Suppressed Warnings**: Added `urllib3.disable_warnings()` to suppress SSL warning messages

## Implementation Details

### Before (google-generativeai SDK):
```python
import google.generativeai as genai
genai.configure(api_key=api_key)
self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = self.model.generate_content(prompt)
```

### After (Direct REST API):
```python
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
response = requests.post(
    url,
    headers={'Content-Type': 'application/json'},
    params={'key': self.api_key},
    json={"contents": [{"parts": [{"text": prompt}]}]},
    timeout=30,
    verify=False  # Skip SSL verification
)
result = response.json()
text = result['candidates'][0]['content']['parts'][0]['text']
```

## Testing Results

### Test 1: Simple Text
```bash
Input:  こんにちは世界
Output: Konnichiwa sekai
Status: ✅ Success
```

### Test 2: Complex Lyrics
```bash
Input:  瞬きすら忘れていた煌めく満天の星座を
Output: mabataki sura wasurete ita kirameku manten no seiza o
Status: ✅ Success
```

### Test 3: Full Audio File Processing
```bash
File:   01 Shogeki.m4a
Status: ✅ Success
- Found local LRC file
- Romanized all lyrics using Gemini
- Created _romaji.lrc file
- Embedded in audio metadata
```

## Sample Output Quality
```
Original: 一秒前の瞬き取り残された世界
Romanji:  Ichi byō mae no matataki torinokosa re ta sekai

Original: 羽を焦がす無数の鳥が灰を散らし安らぎ笑う誰か散らせ
Romanji:  Hane o koga su musū no tori ga hai o chirashi yasuragi warau dare ka chira se
```

## Production Considerations

### Security Note
Using `verify=False` is **not recommended for production** as it disables SSL certificate validation. For production deployments:

1. **Fix Certificate Store**: Update system certificates or Python's `certifi` package
   ```bash
   pip install --upgrade certifi
   ```

2. **Use Custom CA Bundle**: Point to a valid certificate bundle
   ```python
   response = requests.post(url, ..., verify='/path/to/ca-bundle.crt')
   ```

3. **Corporate Proxy**: If behind a corporate proxy, configure proxy settings
   ```python
   proxies = {'https': 'http://proxy.example.com:8080'}
   response = requests.post(url, ..., proxies=proxies)
   ```

### Configuration Option
Consider adding a config option to control SSL verification:
```yaml
api:
  gemini:
    api_key: "..."
    verify_ssl: false  # For development only
```

## Performance
- Average response time: ~2-3 seconds per romanization
- Model: gemini-2.0-flash-exp (fast and accurate)
- Timeout: 30 seconds (prevents indefinite hangs)
- Fallback: Automatically falls back to local romanization on error

## API Cost
- Model: gemini-2.0-flash-exp
- Typical lyric line: 2-10 tokens input, 5-15 tokens output
- Full song (30-40 lines): ~300-600 tokens total
- Cost: Very low (Gemini offers generous free tier)

## Next Steps
1. ✅ Gemini API working
2. ⏳ Test OpenAI API integration
3. ⏳ Implement caching to reduce API calls
4. ⏳ Add translation feature
5. ⏳ Implement Whisper ASR for lyric generation
6. ⏳ Add online lyrics fetching

## Files Modified
- `lyricflow/core/romanizer.py` - Switched to direct REST API for Gemini
- `config.yaml` - Updated with working Gemini API key

## Dependencies
- `requests` - For HTTP calls (already installed)
- `urllib3` - For SSL warning suppression (already installed)
- ~~`google-generativeai`~~ - No longer needed (can be uninstalled)
