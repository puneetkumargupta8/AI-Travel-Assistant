import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-flash-latest")

SYSTEM_PROMPT = """
You are an intent classifier for a travel planning system.

Return ONLY valid JSON.
No explanations.
No extra text.

Supported intents:

1. PLAN
Required fields:
- intent: "PLAN"
- city
- interests (array of strings)
- days (integer)
- pace (relaxed | moderate | packed)

2. EDIT_DAY_PACE
Required fields:
- intent: "EDIT_DAY_PACE"
- day (integer)
- pace (relaxed | moderate | packed)

3. EXPLAIN
Required fields:
- intent: "EXPLAIN"
- target (optional string, name of place or "plan")

If information is missing, infer reasonably.
Assume city is Delhi unless specified otherwise.

If user asks why something was chosen or whether the plan is doable, return intent EXPLAIN.
"""


def clean_json_response(text: str):
    text = text.strip()

    # Remove markdown wrapping if present
    if text.startswith("```"):
        text = text.split("```")[1]

    return text.strip()


def classify_intent(user_text: str):

    try:
        response = model.generate_content(
            SYSTEM_PROMPT + "\nUser: " + user_text,
            request_options={"timeout": 10}
        )

        content = clean_json_response(response.text)

        parsed = json.loads(content)

        return parsed

    except Exception as e:
        return {
            "error": "Intent classification failed",
            "details": str(e)
        }