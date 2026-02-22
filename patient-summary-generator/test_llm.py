"""Live test — calls OpenAI gpt-4o with the mock patient data."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from src.services.validator import validate_and_normalize
from src.services.llm_service import generate_summary
from src.services.post_processor import post_process

MOCK_PATH = os.path.join(os.path.dirname(__file__), "src", "data", "mock_patient.json")

with open(MOCK_PATH) as f:
    mock_patient = json.load(f)


def main():
    model = os.environ.get("FEATHERLESS_MODEL", "deepseek-ai/DeepSeek-V3-0324")
    print(f"Using model: {model}")
    print("API key loaded:", "yes" if os.environ.get("FEATHERLESS_API_KEY") else "NO - check .env file")
    print()

    # Step 1: Validate
    result = validate_and_normalize(mock_patient)
    if not result["valid"]:
        print("Validation failed:", result["errors"])
        sys.exit(1)

    normalized = result["normalized"]
    print("=== Validation passed ===")
    print("Patient:", normalized["patient"]["name"])
    print()

    # Step 2: Call OpenAI (gpt-4o)
    print("=== Calling OpenAI gpt-4o... ===")
    raw_summary = generate_summary(normalized)
    print("Raw LLM response:")
    print(json.dumps(raw_summary, indent=2))
    print()

    # Step 3: Post-process
    processed = post_process(raw_summary, normalized["patient"]["name"])
    print("=== Post-processed summary ===")
    print(json.dumps(processed["summary"], indent=2))
    print()
    print("Word count:", processed["meta"]["word_count"])
    print("Too long:", processed["meta"]["too_long"])
    print()
    print("=== HTML Output ===")
    print(processed["html"])
    print()
    print("=== Test complete! ===")


if __name__ == "__main__":
    main()
