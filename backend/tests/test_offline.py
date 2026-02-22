"""
Offline tests — validates the validator, post-processor, and extraction
parser without calling any external API.
"""

import json
import os
import sys

# Ensure imports resolve from backend root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.validator import validate_and_normalize
from services.post_processor import post_process
from services.extraction_service import parse_transcript, build_llm_prompt

MOCK_PATIENT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "mock_patient.json"
)
TEST_TRANSCRIPT_PATH = os.path.join(
    os.path.dirname(__file__), "..", "data", "test_transcript.json"
)


def test_validator():
    print("=" * 60)
    print("TEST 1: Validate mock patient data")
    print("=" * 60)

    with open(MOCK_PATIENT_PATH) as f:
        mock_patient = json.load(f)

    result = validate_and_normalize(mock_patient)
    print(f"  Valid   : {result['valid']}")
    print(f"  Errors  : {result['errors']}")
    print(f"  Warnings: {result['warnings']}")
    print(f"  Name    : {result['normalized']['patient']['name']}")
    assert result["valid"], "Mock patient should be valid"
    print("  PASSED\n")


def test_reject_missing_name():
    print("=" * 60)
    print("TEST 2: Reject missing patient name")
    print("=" * 60)

    bad = validate_and_normalize({"clinical_data": {}})
    print(f"  Valid : {bad['valid']} (expected False)")
    print(f"  Errors: {bad['errors']}")
    assert not bad["valid"], "Should have rejected missing name"
    print("  PASSED\n")


def test_post_processor():
    print("=" * 60)
    print("TEST 3: Post-process a mock summary (jargon replacement)")
    print("=" * 60)

    fake_llm_response = {
        "greeting": "Hi Margaret! Thank you for coming in today.",
        "what_we_found": (
            "We found that you have hypertension, which means your blood "
            "pressure is higher than normal. You also had some dyspnea, "
            "or difficulty breathing."
        ),
        "your_vitals": "BP 142/88, HR 94, Temp 98.6°F, O2 96%.",
        "your_medications": "Lisinopril 10mg once daily for blood pressure.",
        "watch_for": "Chest pain, worsening shortness of breath, leg swelling.",
        "next_steps": "Return in 2 weeks or sooner if symptoms worsen.",
        "closing": "Take care Margaret, you are in good hands!",
    }

    processed = post_process(fake_llm_response, "Margaret Williams")
    print(f"  Word count: {processed['meta']['word_count']}")
    print(f"  Too long  : {processed['meta']['too_long']}")

    # Verify jargon was replaced
    assert "hypertension" not in processed["summary"]["what_we_found"], \
        "Jargon 'hypertension' should have been replaced"
    assert "dyspnea" not in processed["summary"]["what_we_found"], \
        "Jargon 'dyspnea' should have been replaced"

    print("  Jargon replacement verified")
    print("  PASSED\n")


def test_transcript_parser():
    print("=" * 60)
    print("TEST 4: Parse transcript (doctor/patient separation)")
    print("=" * 60)

    with open(TEST_TRANSCRIPT_PATH) as f:
        transcript_data = json.load(f)

    parsed = parse_transcript(transcript_data)
    print(f"  Session ID       : {parsed['session_id']}")
    print(f"  Doctor lines     : {len(parsed['doctor_lines'])}")
    print(f"  Patient lines    : {len(parsed['patient_lines'])}")
    print(f"  Conversation turns: {len(parsed['conversation'])}")

    assert len(parsed["doctor_lines"]) == 7, \
        f"Expected 7 doctor lines, got {len(parsed['doctor_lines'])}"
    assert len(parsed["patient_lines"]) == 5, \
        f"Expected 5 patient lines, got {len(parsed['patient_lines'])}"

    # Test LLM prompt builder
    prompt = build_llm_prompt(parsed["conversation"])
    assert prompt.startswith("Doctor:"), "Prompt should start with 'Doctor:'"
    print(f"  LLM prompt length: {len(prompt)} chars")
    print("  PASSED\n")


if __name__ == "__main__":
    test_validator()
    test_reject_missing_name()
    test_post_processor()
    test_transcript_parser()

    print("=" * 60)
    print("ALL OFFLINE TESTS PASSED")
    print("=" * 60)
