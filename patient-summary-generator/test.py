"""Offline tests — validates the validator and post-processor without calling OpenAI."""

import json
import os
import sys

# Ensure imports resolve from project root
sys.path.insert(0, os.path.dirname(__file__))

from src.services.validator import validate_and_normalize
from src.services.post_processor import post_process

MOCK_PATH = os.path.join(os.path.dirname(__file__), "src", "data", "mock_patient.json")

with open(MOCK_PATH) as f:
    mock_patient = json.load(f)


# ── Test 1: Validate mock patient data ──────────────────────────────────────
print("=== Test 1: Validate mock patient data ===")
result = validate_and_normalize(mock_patient)

print("Valid:", result["valid"])
print("Errors:", result["errors"])
print("Warnings:", result["warnings"])
print("Normalized patient name:", result["normalized"]["patient"]["name"])
print("Normalized visit date:", result["normalized"]["visit"]["date"])
print("Diagnoses count:", len(result["normalized"]["clinical_data"]["diagnoses"]))
print()

if not result["valid"]:
    print("FAIL: Mock patient should be valid")
    sys.exit(1)


# ── Test 2: Reject missing patient name ─────────────────────────────────────
print("=== Test 2: Reject missing patient name ===")
bad = validate_and_normalize({"clinical_data": {}})
print(f"Valid: {bad['valid']} (expected False)")
print("Errors:", bad["errors"])
print()

if bad["valid"]:
    print("FAIL: Should have rejected missing patient name")
    sys.exit(1)


# ── Test 3: Post-process a simulated LLM response ──────────────────────────
print("=== Test 3: Post-process a mock summary ===")
fake_llm_response = {
    "greeting": "Hi Margaret! Thank you for coming in today.",
    "what_we_found": (
        "We found that you have hypertension, which means your blood pressure "
        "is higher than normal. You also had some dyspnea, or difficulty breathing."
    ),
    "your_vitals": "Your blood pressure was 142/88, heart rate 94, temperature 98.6°F, and oxygen level 96%.",
    "your_medications": "We prescribed Lisinopril 10mg once daily to help lower your blood pressure.",
    "watch_for": "Please watch for any chest pain, worsening shortness of breath, or swelling in your legs.",
    "next_steps": "Come back in 2 weeks or sooner if your symptoms get worse.",
    "closing": "Take care Margaret, you are in good hands!",
}

processed = post_process(fake_llm_response, result["normalized"]["patient"]["name"])

print("Jargon-replaced summary:")
print(json.dumps(processed["summary"], indent=2))
print()
print("Word count:", processed["meta"]["word_count"])
print("Too long:", processed["meta"]["too_long"])
print()
print("HTML preview (first 200 chars):")
print(processed["html"][:200] + "...")
print()

# Verify jargon was replaced
if "hypertension" in processed["summary"]["what_we_found"]:
    print("FAIL: Jargon 'hypertension' should have been replaced")
    sys.exit(1)

if "dyspnea" in processed["summary"]["what_we_found"]:
    print("FAIL: Jargon 'dyspnea' should have been replaced")
    sys.exit(1)

print("=== All tests passed! ===")
