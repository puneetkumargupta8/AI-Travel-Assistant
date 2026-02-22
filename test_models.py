import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

print("Available models:")
try:
    models = genai.list_models()
    for model in models:
        print(f"  - {model.name}")
except Exception as e:
    print(f"Error listing models: {e}")

print("\nTesting different model names:")
test_models = ["gemini-1.5-flash", "gemini-pro", "models/gemini-1.5-flash", "models/gemini-pro"]

for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hello")
        print(f"✓ {model_name}: {response.text[:50]}")
        break
    except Exception as e:
        print(f"✗ {model_name}: {str(e)[:100]}")