# Musixmatch Captcha Issue - IMPORTANT ⚠️

## Issue
Musixmatch API is returning captcha challenges (`status_code: 401, hint: 'captcha'`) when attempting to fetch tokens.

## Root Cause
Musixmatch has implemented anti-bot measures that detect automated API access:
1. **Rate Limiting:** Too many requests from the same IP
2. **User Agent Detection:** Missing or suspicious user agents  
3. **Token Management:** Stricter token validation

## Current Status
- ✅ **LRCLIB:** Working perfectly, free, no authentication required
- ⚠️ **Musixmatch:** Intermittent captcha challenges, may require manual intervention

## Fixes Implemented

### 1. Enhanced Token Handling
```python
# Handle both dict and list responses
if isinstance(body, list):
    if not body:
        logger.error("Token response body is empty list")
        return None
    body = body[0] if len(body) > 0 else {}
```

### 2. Updated User Agent
```python
self.headers = {
    'authority': 'apic-desktop.musixmatch.com',
    'cookie': 'x-mxm-token-guid=',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Musixmatch/4.10.55 Chrome/120.0.6099.291 Electron/28.2.3 Safari/537.36'
}
```

### 3. Rate Limiting
```python
self._min_request_interval = 0.5  # 500ms between requests

def _make_request(self, endpoint: str, params: Dict[str, Any]):
    # Wait if needed
    elapsed = time.time() - self._last_request_time
    if elapsed < self._min_request_interval:
        time.sleep(self._min_request_interval - elapsed)
```

### 4. Better Error Logging
```python
if data:
    logger.debug(f"Token response: {data}")
    message = data.get('message', {})
    header = message.get('header', {})
    
    if header.get('status_code') == 401:
        logger.error(f"Captcha required: {header.get('hint')}")
```

## Workarounds

### Option 1: Use LRCLIB (Recommended)
```bash
# LRCLIB is the default, no captcha issues
python -m lyricflow.cli.main fetch -t "Song" -a "Artist"

# Or explicitly specify:
python -m lyricflow.cli.main fetch -t "Song" -a "Artist" --provider lrclib
```

### Option 2: Manual Musixmatch Token
If you have a valid Musixmatch token from the desktop app:

1. Extract token from Musixmatch desktop app
2. Set environment variable:
   ```powershell
   $env:MUSIXMATCH_TOKEN = "your_token_here"
   ```
3. Update code to use it:
   ```python
   import os
   token = os.environ.get('MUSIXMATCH_TOKEN')
   api = MusixmatchAPI(token=token)
   ```

### Option 3: Wait and Retry
Captcha challenges may be temporary:
```bash
# Wait a few minutes and try again
python -m lyricflow.cli.main fetch -t "Song" -a "Artist" --provider musixmatch
```

## Recommendations

### For Users
1. **Use LRCLIB as default** - It's free, reliable, and has no rate limits
2. **Only use Musixmatch when:**
   - You need translation features
   - Song not available on LRCLIB
   - You have a valid token from the desktop app

### For Developers
1. **Implement token caching** - Save valid tokens to avoid repeated requests
2. **Add retry logic** - Exponential backoff for failed token requests
3. **Fallback mechanism** - Auto-switch to LRCLIB if Musixmatch fails
4. **User notification** - Clearly inform users about provider limitations

## Technical Details

### Captcha Response Example
```json
{
  "message": {
    "header": {
      "status_code": 401,
      "execute_time": 0.007,
      "hint": "captcha"
    }
  }
}
```

### Successful Token Response
```json
{
  "message": {
    "header": {"status_code": 200},
    "body": {
      "user_token": "251019fe46d4524a8bf05ca93b0c056e3ebdacef897b8c563f726d",
      "app_config": {...}
    }
  }
}
```

## Testing

### Test LRCLIB (Should Work)
```bash
python -m lyricflow.cli.main fetch --provider lrclib --title "Soul's Refrain" --artist "米津玄師"
```

### Test Musixmatch (May Show Captcha)
```bash
python -m lyricflow.cli.main -v fetch --provider musixmatch --title "Soul's Refrain" --artist "米津玄師"
```

## Future Improvements

### Short Term
1. ✅ Implement better error messages
2. ✅ Add rate limiting
3. ⏳ Token caching to disk
4. ⏳ Auto-fallback to LRCLIB

### Long Term
1. Implement proper OAuth flow (if Musixmatch provides it)
2. Add proxy support for rotating IPs
3. Implement session management
4. Add CAPTCHA solver integration (if legally allowed)

## Status Summary

- **Issue Identified:** ✅ Musixmatch captcha challenges
- **Root Cause:** ✅ Anti-bot measures
- **Workarounds:** ✅ Use LRCLIB, manual tokens, rate limiting
- **Long-term Fix:** ⏳ Pending Musixmatch API changes or OAuth support

---

**Recommendation:** Use LRCLIB as the primary provider. Musixmatch should be considered a secondary option for when translations are needed or LRCLIB doesn't have the song.

**Date:** 2025-01-27  
**Severity:** Medium (workaround available)  
**Impact:** Users can still fetch lyrics via LRCLIB
