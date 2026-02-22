import json
import os

from openai import OpenAI

from src.prompts.system_prompt import build_system_prompt

FEATHERLESS_BASE_URL = "https://api.featherless.ai/v1"

client = OpenAI(
    base_url=FEATHERLESS_BASE_URL,
    api_key=os.environ.get("FEATHERLESS_API_KEY", ""),
)

MODEL = os.environ.get("FEATHERLESS_MODEL", "deepseek-ai/DeepSeek-V3-0324")


def generate_summary(normalized_data):
    language = normalized_data["patient"].get("preferred_language", "en")
    system_prompt = build_system_prompt(language)

    user_message = (
        "Please generate a patient-friendly visit summary for the following clinical data:\n\n"
        f"{json.dumps(normalized_data, indent=2)}\n\n"
        "Remember: output only the JSON object. No extra text."
    )

    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1000,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    raw_text = response.choices[0].message.content

    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        cleaned = raw_text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
