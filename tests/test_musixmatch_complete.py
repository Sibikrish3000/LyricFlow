"""
Test for Musixmatch and logging issues in TUI.
"""

import sys
import logging
import os

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

print("="*60)
print("Testing Musixmatch Provider + Logging")
print("="*60)

# Set up logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)

print("\n1. Testing UnifiedLyricsFetcher with Musixmatch")
print("-"*60)

from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher

try:
    fetcher = UnifiedLyricsFetcher(provider="musixmatch")
    print("✅ Musixmatch fetcher created")
    
    print("\n2. Testing fetch() method")
    print("-"*60)
    result = fetcher.fetch("Yesterday", "The Beatles")
    
    print(f"\nResult type: {type(result)}")
    
    if result is None:
        print("❌ No result returned")
    elif isinstance(result, dict):
        print("✅ Result is a dict (correct)")
        print(f"  - Title: {result.get('title')}")
        print(f"  - Artist: {result.get('artist')}")
        print(f"  - Has synced: {result.get('has_synced')}")
        print(f"  - Has plain: {result.get('has_plain')}")
        print(f"  - Provider: {result.get('provider')}")
    elif isinstance(result, list):
        print("❌ Result is a list (BUG)")
        print(f"  List length: {len(result)}")
        if result:
            print(f"  First item type: {type(result[0])}")
            print(f"  First item: {result[0]}")
    else:
        print(f"⚠️ Unexpected type: {type(result)}")
    
    print("\n3. Testing dict access")
    print("-"*60)
    if isinstance(result, dict):
        try:
            title = result.get('title')
            print(f"✅ .get('title') works: {title}")
            
            duration = result.get('duration')
            if duration:
                dur = int(duration)
                duration_str = f"{dur // 60}:{dur % 60:02d}"
                print(f"✅ Duration formatting works: {duration_str}")
            
            print("✅ All dict operations successful")
        except Exception as e:
            print(f"❌ Error accessing dict: {e}")
    
    print("\n4. Testing search() method")
    print("-"*60)
    results = fetcher.search("Yesterday", "The Beatles")
    print(f"Search results type: {type(results)}")
    print(f"Number of results: {len(results) if isinstance(results, list) else 'N/A'}")
    
    if isinstance(results, list) and results:
        print(f"First result type: {type(results[0])}")
        if isinstance(results[0], dict):
            print("✅ Search returns list of dicts")
        else:
            print("⚠️ Search returns list of non-dicts")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("5. Testing logging suppression")
print("="*60)

print("\nBefore suppression:")
logger = logging.getLogger('lyricflow')
logger.info("This message should appear")

print("\nAfter suppression (simulating TUI launch):")
root_logger = logging.getLogger()
original_handlers = root_logger.handlers[:]

# Remove stream handlers
for handler in original_handlers:
    if isinstance(handler, logging.StreamHandler) and hasattr(handler, 'stream'):
        if handler.stream in (sys.stdout, sys.stderr):
            root_logger.removeHandler(handler)
            print(f"  Removed handler: {handler}")

logger.info("This message should NOT appear in console")
print("✅ Logging suppression working (message above not visible)")

# Restore
for handler in original_handlers:
    if handler not in root_logger.handlers:
        root_logger.addHandler(handler)

logger.info("This message should appear again")

print("\n" + "="*60)
print("Test Complete")
print("="*60)
