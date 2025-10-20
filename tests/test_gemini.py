#!/usr/bin/env python3
"""Test Gemini API directly."""

import google.generativeai as genai

# Configure with your API key
api_key = "AIzaSyAIy4CNtIVae_7KYDu6eS85ro51U40AVBw"
genai.configure(api_key=api_key)

print("Testing Gemini API...")
print(f"API Key: {api_key[:20]}...")

# Try different model names
model_names = [
    'gemini-2.0-flash-exp',
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro',
]

for model_name in model_names:
    print(f"\nTrying model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Romanize this Japanese text: こんにちは")
        print(f"✅ Success with {model_name}!")
        print(f"Response: {response.text}")
        break
    except Exception as e:
        print(f"❌ Failed with {model_name}: {e}")

print("\n" + "="*60)
print("Testing list models...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")
except Exception as e:
    print(f"Error listing models: {e}")
