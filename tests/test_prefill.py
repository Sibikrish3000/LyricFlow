"""
Test pre-filling functionality in TUI
"""

print("""
╔══════════════════════════════════════════════════════════╗
║         TUI Pre-filling Test                             ║
╔══════════════════════════════════════════════════════════╗

This will test three scenarios:

1. TUI with no parameters (empty fields)
2. TUI with pre-filled title and artist
3. TUI with audio file (auto-fill from metadata)

Press Enter to continue...
""")

input()

from lyricflow.tui import launch_tui
from pathlib import Path

print("\n" + "="*60)
print("Test 1: Empty TUI (no pre-fill)")
print("="*60)
print("All fields should be empty.")
print("Press Ctrl+C to exit and continue to next test...\n")

try:
    launch_tui()
except KeyboardInterrupt:
    print("\n✅ Test 1 complete\n")

print("\n" + "="*60)
print("Test 2: Pre-filled Title and Artist")
print("="*60)
print("Title field should show: 'Yesterday'")
print("Artist field should show: 'The Beatles'")
print("Press Ctrl+C to exit and continue to next test...\n")

try:
    launch_tui(
        initial_title="Yesterday",
        initial_artist="The Beatles"
    )
except KeyboardInterrupt:
    print("\n✅ Test 2 complete\n")

print("\n" + "="*60)
print("Test 3: Pre-filled with Provider")
print("="*60)
print("Title: 'Bohemian Rhapsody'")
print("Artist: 'Queen'")
print("Album: 'A Night at the Opera'")
print("Provider: Musixmatch (radio button selected)")
print("Press Ctrl+C to exit...\n")

try:
    launch_tui(
        provider="musixmatch",
        initial_title="Bohemian Rhapsody",
        initial_artist="Queen",
        initial_album="A Night at the Opera"
    )
except KeyboardInterrupt:
    print("\n✅ Test 3 complete\n")

print("\n" + "="*60)
print("✅ All tests complete!")
print("="*60)
print("""
Summary:
- Empty TUI works
- Pre-filled title/artist works
- Pre-filled with provider selection works

Now test CLI integration:

# Without title (should launch TUI)
lyricflow fetch -i

# With title (should pre-fill TUI)
lyricflow fetch -i -t "Yesterday" -a "Beatles"

# With audio file (should launch TUI)
lyricflow fetch -i --audio song.m4a
""")
