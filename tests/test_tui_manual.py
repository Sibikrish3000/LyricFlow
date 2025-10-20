"""
Manual TUI test - check if logging fix works
"""
import sys
from pathlib import Path

# Add project to path if needed
sys.path.insert(0, str(Path(__file__).parent))

print("Importing TUI...")
from lyricflow.tui import launch_tui

print("Launching TUI with logging disabled...")
print("Try searching for 'Yesterday' by 'The Beatles'")
print("Press Ctrl+C to exit\n")

try:
    launch_tui(provider="lrclib")
except KeyboardInterrupt:
    print("\n\nTUI closed.")
except Exception as e:
    print(f"\n\nError: {e}")
    import traceback
    traceback.print_exc()
