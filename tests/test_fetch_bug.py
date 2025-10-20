"""
Quick test to reproduce the TUI fetch bug
"""

import sys

print("Testing fetch functionality...")

# Test 1: Check what fetch() returns
from lyricflow.core.lyrics_provider import create_fetcher

print("\n1. Testing LRCLIB fetch...")
fetcher = create_fetcher("lrclib")
result = fetcher.fetch("Yesterday", "The Beatles")

print(f"   Type of result: {type(result)}")
print(f"   Is dict: {isinstance(result, dict)}")
print(f"   Is list: {isinstance(result, list)}")

if result:
    print(f"   Title: {result.get('title')}")
    print(f"   Has .get() method: {hasattr(result, 'get')}")
else:
    print("   Result is None")

# Test 2: Check what happens when wrapped in list
print("\n2. Testing list wrapping...")
if result:
    results_list = [result]
    print(f"   Type of results_list: {type(results_list)}")
    print(f"   Length: {len(results_list)}")
    print(f"   First item type: {type(results_list[0])}")
    print(f"   First item is dict: {isinstance(results_list[0], dict)}")
    
    # Try accessing like in TUI
    try:
        first_result = results_list[0]
        title = first_result.get('title')
        print(f"   ✅ Can access first_result.get('title'): {title}")
    except AttributeError as e:
        print(f"   ❌ Error accessing: {e}")

print("\n3. Testing if UnifiedLyricsFetcher.fetch returns correct type...")
from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher

ulf = UnifiedLyricsFetcher(provider="lrclib")
result2 = ulf.fetch("Yesterday", "The Beatles")

print(f"   Type: {type(result2)}")
print(f"   Is dict: {isinstance(result2, dict)}")
if result2:
    try:
        print(f"   Title: {result2.get('title')}")
        print("   ✅ No error!")
    except AttributeError as e:
        print(f"   ❌ Error: {e}")

print("\nTest complete!")
