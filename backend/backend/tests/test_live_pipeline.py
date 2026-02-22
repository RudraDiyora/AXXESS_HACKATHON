"""
Live pipeline test — calls the Featherless LLM to extract clinical data
from the test transcript and then generates a patient summary.

Requires FEATHERLESS_API_KEY to be set in .env.
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from services.extraction_service import run_extraction
from services.validator import validate_and_normalize
from services.summary_service import generate_summary
from services.post_processor import post_process

TEST_TRANSCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "test_transcript.json"
)


def main():
    print("=" * 60)
    print("LIVE PIPELINE TEST  (LLM calls enabled)")
    print("=" * 60)

    api_key = os.environ.get("FEATHERLESS_API_KEY", "")
    model = os.environ.get("FEATHERLESS_MODEL", "deepseek-ai/DeepSeek-V3-0324")
    print(f"  Model  : {model}")
    print(f"  API key: {'loaded' if api_key else 'MISSING — check .env'}")
    print()

    # Load test transcript
    with open(TEST_TRANSCRIPT_PATH) as f:
        transcript_data = json.load(f)

    # ── Stage 1: Clinical extraction ────────────────────────────────────
    print("[1/3] Extracting clinical data from transcript...")
    clinical_json = run_extraction(transcript_data)
    print("      Done!")
    print(json.dumps(clinical_json, indent=2))
    print()

    # ── Stage 2: Validate ───────────────────────────────────────────────
    print("[2/3] Validating...")
    validation = validate_and_normalize(clinical_json)
    print(f"      Valid   : {validation['valid']}")
    print(f"      Warnings: {validation['warnings']}")

    if not validation["valid"]:
        print(f"      Errors: {validation['errors']}")
        sys.exit(1)
    print()

    # ── Stage 3: Summary generation ─────────────────────────────────────
    print("[3/3] Generating patient-friendly summary...")
    normalized = validation["normalized"]
    raw_summary = generate_summary(normalized)
    processed = post_process(raw_summary, normalized["patient"]["name"])
    print("      Done!")
    print()

    print("--- Summary JSON ---")
    print(json.dumps(processed["summary"], indent=2))
    print()

    print(f"--- Meta ---")
    print(f"  Word count: {processed['meta']['word_count']}")
    print(f"  Too long  : {processed['meta']['too_long']}")
    print(f"  Flags     : {processed['meta']['flagged']}")
    print()

    print("--- HTML ---")
    print(processed["html"])
    print()

    print("=" * 60)
    print("LIVE PIPELINE TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
