"""Direct test of romanizer newline preservation."""
from lyricflow.core.romanizer import Romanizer

print("=" * 60)
print("Direct Romanizer Test")
print("=" * 60)

# Initialize romanizer
r = Romanizer()

# Test input
text = "[04:19.54]奇跡は起こるよ 何度でも\n[04:25.94]魂のルフラン"

print("\nInput text (repr):")
print(repr(text))

print("\nInput text (formatted):")
print(text)

# Romanize
result = r.romanize(text, 'ja', use_ai=False)

print("\n" + "=" * 60)
print("Romanized Output")
print("=" * 60)

print("\nRomanized text (repr):")
print(repr(result))

print("\nRomanized text (formatted):")
print(result)

print("\n" + "=" * 60)
print("Verification")
print("=" * 60)

if "\n" in result:
    print("✓ SUCCESS: Newlines are preserved!")
    lines = result.split("\n")
    print(f"✓ Number of lines: {len(lines)}")
    for i, line in enumerate(lines, 1):
        print(f"  Line {i}: {line}")
else:
    print("✗ FAILED: Newlines are missing!")
