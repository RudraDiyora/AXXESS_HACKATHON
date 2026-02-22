"""
Patient-friendly summary generation via Featherless LLM.

Source: Patient_Summary_Generator branch (src/services/llm_service.py)
"""

import json
import os

from openai import OpenAI

from config import FEATHERLESS_API_KEY, FEATHERLESS_BASE_URL, FEATHERLESS_MODEL
from prompts.system_prompt import build_summary_prompt

client = OpenAI(
    base_url=FEATHERLESS_BASE_URL,
    api_key=FEATHERLESS_API_KEY,
)


def generate_summary(normalized_data: dict) -> dict:
    """
    Takes validated/normalised clinical data and returns a patient-friendly
    summary as a dict with keys: greeting, what_we_found, your_vitals,
    your_medications, watch_for, next_steps, closing.
    """
    language = normalized_data.get("patient", {}).get("preferred_language", "en")
    system_prompt = build_summary_prompt(language)

    user_message = (
        "Please generate a patient-friendly visit summary for the "
        "following clinical data:\n\n"
        f"{json.dumps(normalized_data, indent=2)}\n\n"
        "Remember: output only the JSON object. No extra text."
    )

    response = client.chat.completions.create(
        model=FEATHERLESS_MODEL,
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
