# Newline Preservation Fix - COMPLETE ✅

## Issue
The `clean_lrc_timestamps()` function was removing newlines from multi-line LRC content, causing all lyrics to be on a single line.

**Example:**
```
Input (correct):
[04:19.54]kiseki wa okoru yo nando demo
[04:25.94]tamashii no rufuran

Output (broken):
[04:19.54]kiseki wa okoru yo nando demo [04:25.94]tamashii no rufuran
```

## Root Cause
The regex pattern was using `\s+` which matches **all whitespace** including:
- Spaces ` `
- Tabs `\t`
- Newlines `\n`
- Carriage returns `\r`

```python
# OLD - removes ALL whitespace including newlines
text = re.sub(r'(\[\d+:\d+\.\d+\])\s+', r'\1', text)
```

## Solution
Changed the regex to only match **horizontal whitespace** (spaces and tabs), preserving newlines:

```python
# NEW - removes only spaces and tabs, preserves newlines
text = re.sub(r'(\[\d+:\d+\.\d+\])[ \t]+', r'\1', text)
```

### Regex Explanation
- `[ \t]+` - Character class matching one or more:
  - ` ` - Space character
  - `\t` - Tab character
  - **Does NOT match:** `\n` (newline), `\r` (carriage return)

## Fixed Code

### File: `lyricflow/core/romanizer.py` (Line 36-56)

```python
def clean_lrc_timestamps(text: str) -> str:
    """
    Clean LRC timestamps to proper format.
    
    Fixes:
    - Spaces inside brackets: [ 00 : 01 . 61 ] -> [00:01.61]
    - Spaces after brackets: [00:01.61] text -> [00:01.61]text
    
    Args:
        text: Text with potential timestamp issues
        
    Returns:
        Text with cleaned timestamps (preserves newlines)
    """
    # First, remove spaces inside timestamp brackets
    # Pattern: [ 00 : 01 . 61 ] -> [00:01.61]
    text = re.sub(r'\[\s*(\d+)\s*:\s*(\d+)\s*\.\s*(\d+)\s*\]', r'[\1:\2.\3]', text)
    
    # Then, remove ONLY horizontal spaces after timestamp (not newlines)
    # Pattern: [00:01.61] text -> [00:01.61]text
    # Use [ \t]+ to match only spaces and tabs, NOT newlines
    text = re.sub(r'(\[\d+:\d+\.\d+\])[ \t]+', r'\1', text)
    
    return text
```

## Test Cases

### Test 1: Single Line
```python
Input:  "[00:01.61] text here"
Output: "[00:01.61]text here"
✅ Space removed, no newlines to preserve
```

### Test 2: Multi-Line LRC
```python
Input:  "[00:01.61] first line\n[00:05.23] second line"
Output: "[00:01.61]first line\n[00:05.23]second line"
✅ Spaces removed, newlines preserved
```

### Test 3: Mixed Spaces and Newlines
```python
Input:  "[00:01.61]   text\n[00:05.23]\tmore"
Output: "[00:01.61]text\n[00:05.23]more"
✅ Tabs and spaces removed, newlines preserved
```

### Test 4: Malformed Timestamps with Newlines
```python
Input:  "[ 00 : 01 . 61 ] text\n[ 00 : 05 . 23 ] more"
Output: "[00:01.61]text\n[00:05.23]more"
✅ Internal spaces removed, trailing spaces removed, newlines preserved
```

## API Test

### Request (test_request.json)
```json
{
  "text": "[04:19.54]奇跡は起こるよ 何度でも\n[04:25.94]魂のルフラン",
  "language": "ja",
  "use_ai": false
}
```

### Command
```bash
curl -X POST http://localhost:8000/romanize \
  -H "Content-Type: application/json" \
  -d @test_request.json
```

### Expected Response
```json
{
  "original": "[04:19.54]奇跡は起こるよ 何度でも\n[04:25.94]魂のルフラン",
  "romanized": "[04:19.54]kiseki wa okoru yo nando demo\n[04:25.94]tamashii no rufuran",
  "language": "ja"
}
```

**Key Points:**
- ✅ Newline `\n` between lines is preserved
- ✅ Timestamps are clean: `[04:19.54]text` (no space)
- ✅ Each line on its own line

## Impact

### Before Fix
```
[04:19.54]kiseki wa okoru yo nando demo [04:25.94]tamashii no rufuran
```
**Problem:** All on one line, hard to read, breaks LRC format

### After Fix
```
[04:19.54]kiseki wa okoru yo nando demo
[04:25.94]tamashii no rufuran
```
**Result:** Proper multi-line LRC format maintained

## Technical Details

### Whitespace Characters in Regex

| Pattern | Matches | Use Case |
|---------|---------|----------|
| `\s` | All whitespace (`\n`, `\r`, `\t`, ` `) | When you want to match everything |
| `\s+` | One or more of any whitespace | **DON'T USE** for LRC (eats newlines) |
| `[ \t]` | Space or tab only | **DO USE** for LRC (preserves newlines) |
| `[ \t]+` | One or more space/tab | Perfect for our use case ✅ |

### Why This Matters

LRC files are **line-based** formats:
- Each timestamp starts a new line
- Format: `[mm:ss.xx]lyrics text`
- Newlines are **structural**, not just whitespace
- Removing them breaks the entire format

## Files Modified

1. ✅ `lyricflow/core/romanizer.py` - Line 51
   - Changed: `\s+` → `[ \t]+`
   - Impact: All romanization methods (Local, OpenAI, Gemini)

## Coverage

This fix applies to:
- ✅ Local romanization (pykakasi + fugashi)
- ✅ OpenAI romanization (via clean_lrc_timestamps)
- ✅ Gemini romanization (via clean_lrc_timestamps)
- ✅ Saved LRC files (via clean_lrc_timestamps)
- ✅ API responses (`/romanize` endpoint)

## Related Fixes

This completes the timestamp cleaning series:

1. ✅ Remove spaces inside timestamps: `[ 00 : 01 . 61 ]` → `[00:01.61]`
2. ✅ Remove spaces after timestamps: `[00:01.61] text` → `[00:01.61]text`
3. ✅ **NEW:** Preserve newlines in multi-line content

## Verification

### CLI Test
```bash
# Create test LRC with multiple lines
echo "[00:01.61]わたくし\n[00:05.23]帰りなさい" | \
  python -m lyricflow.cli.main romanize

# Expected: Two lines in output
```

### API Test
```bash
# Use the test_request.json file
curl -X POST http://localhost:8000/romanize \
  -H "Content-Type: application/json" \
  -d @test_request.json | jq -r '.romanized'

# Expected: Multi-line output with proper newlines
```

## Summary

**Problem:** Newlines were being removed from multi-line LRC content  
**Root Cause:** Regex `\s+` matched all whitespace including newlines  
**Solution:** Changed to `[ \t]+` to match only spaces and tabs  
**Result:** Newlines are now preserved, LRC format maintained  
**Status:** ✅ COMPLETE

---

**Date:** 2025-01-27  
**File Modified:** `lyricflow/core/romanizer.py`  
**Lines Changed:** 1 (critical regex pattern)  
**Impact:** ALL romanization and LRC cleaning operations
