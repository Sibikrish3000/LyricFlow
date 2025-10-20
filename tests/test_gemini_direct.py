"""Direct test of Gemini REST API."""
import requests
import json

api_key = "AIzaSyAIy4CNtIVae_7KYDu6eS85ro51U40AVBw"

print("Testing Gemini API with requests...")

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
headers = {
    'Content-Type': 'application/json',
}
params = {
    'key': api_key
}
data = {
    "contents": [{
        "parts": [{
            "text": "Say hello"
        }]
    }]
}

print(f"URL: {url}")
print(f"Sending request...")

try:
    response = requests.post(url, headers=headers, params=params, json=data, timeout=10, verify=False)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\nSuccess! Response text:")
        print(result['candidates'][0]['content']['parts'][0]['text'])
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {type(e).__name__}: {e}")
