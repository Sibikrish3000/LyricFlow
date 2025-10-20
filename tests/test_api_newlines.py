"""Test script to verify API preserves newlines correctly."""
import requests
import json

# Test data
test_input = {
    "text": "[04:19.54]奇跡は起こるよ 何度でも\n[04:25.94]魂のルフラン",
    "language": "ja",
    "use_ai": False
}

print("=" * 60)
print("Testing API with multi-line LRC content")
print("=" * 60)

print("\nInput text:")
print(repr(test_input["text"]))
print("\nFormatted input:")
print(test_input["text"])

# Make API request
response = requests.post(
    "http://localhost:8000/romanize",
    headers={"Content-Type": "application/json"},
    json=test_input
)

print("\n" + "=" * 60)
print("API Response:")
print("=" * 60)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    romanized = result["romanized"]
    
    print("\nRomanized text (repr):")
    print(repr(romanized))
    
    print("\nRomanized text (formatted):")
    print(romanized)
    
    print("\n" + "=" * 60)
    print("Verification:")
    print("=" * 60)
    
    if "\n" in romanized:
        print("✓ Newlines are PRESERVED")
        lines = romanized.split("\n")
        print(f"✓ Number of lines: {len(lines)}")
        for i, line in enumerate(lines, 1):
            print(f"  Line {i}: {line}")
    else:
        print("✗ Newlines are MISSING")
        print("  API server may need to be restarted!")
else:
    print(f"\nError: {response.text}")
