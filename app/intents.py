import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


SYSTEM_PROMPT = """
You are an intent classifier for a travel planning system.

Return ONLY valid JSON.
No explanations.
No extra text.

Supported intents:

1. PLAN
Required fields:
- city
- interests (array of strings)
- days (integer)
- pace (relaxed | moderate | packed)

2. EDIT_DAY_PACE
Required fields:
- day (integer)
- pace (relaxed | moderate | packed)

If information is missing, infer reasonably.
Assume city is Delhi unless specified otherwise.
"""


def classify_intent(user_text: str):

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    )

    content = response.choices[0].message.content

    try:
        parsed = json.loads(content)
        return parsed
    except Exception:
        return {"error": "Failed to parse intent", "raw": content}