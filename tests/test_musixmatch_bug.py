"""Test to reproduce the Musixmatch list error."""

from lyricflow.core.lyrics_provider import UnifiedLyricsFetcher

print("Testing Musixmatch provider...")
fetcher = UnifiedLyricsFetcher(provider="musixmatch")

print("\n1. Testing fetch method (should return dict):")
result = fetcher.fetch("Yesterday", "The Beatles")

print(f"Type of result: {type(result)}")
print(f"Result: {result}")

if isinstance(result, dict):
    print("✅ Result is a dict (correct)")
    print(f"Title: {result.get('title')}")
    print(f"Artist: {result.get('artist')}")
elif isinstance(result, list):
    print("❌ Result is a list (BUG!)")
else:
    print(f"⚠️ Result is {type(result)} (unexpected)")
