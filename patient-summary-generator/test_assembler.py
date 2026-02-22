"""End-to-end test for the patient assembler.

Verifies:
1. The assembler takes an input WITHOUT diagnoses and produces a complete
   JSON in mock_patient.json format.
2. The assembled JSON passes the validator.
3. The assembled JSON works through the post-processor with a fake LLM
   response (no API key required).
"""

import json
import os
import sys

# Ensure imports resolve from project root
sys.path.insert(0, os.path.dirname(__file__))

from src.services.patient_assembler import assemble_patient_json
from src.services.validator import validate_and_normalize
from src.services.post_processor import post_process

# ── Paths ────────────────────────────────────────────────────────────────────
TEST_INPUT_PATH = os.path.join(
    os.path.dirname(__file__), "src", "data", "test_input.json",
)
MOCK_PATIENT_PATH = os.path.join(
    os.path.dirname(__file__), "src", "data", "mock_patient.json",
)

passed = 0
failed = 0


def check(label, condition, detail=""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  ✓ {label}")
    else:
        failed += 1
        msg = f"  ✗ {label}"
        if detail:
            msg += f" — {detail}"
        print(msg)


# ── Load test input ─────────────────────────────────────────────────────────
print("Loading test input (no diagnoses)…")
with open(TEST_INPUT_PATH) as f:
    test_input = json.load(f)

check(
    "Input has no diagnoses",
    "diagnoses" not in test_input.get("clinical_data", {}),
)
print()

# ── Test 1: Assembler produces complete JSON ─────────────────────────────────
print("=== Test 1: Assemble patient JSON ===")
assembled = assemble_patient_json(test_input)
print(json.dumps(assembled, indent=2))
print()

check(
    "Top-level keys match mock_patient.json",
    set(assembled.keys()) == {"patient", "clinical_data"},
    f"got {set(assembled.keys())}",
)

cd = assembled.get("clinical_data", {})
expected_keys = {
    "chief_complaint", "vitals", "symptoms",
    "diagnoses", "medications_prescribed", "follow_up",
}
check(
    "clinical_data keys match mock format",
    set(cd.keys()) == expected_keys,
    f"got {set(cd.keys())}",
)

check(
    "Diagnoses were generated",
    len(cd.get("diagnoses", [])) > 0,
    f"count = {len(cd.get('diagnoses', []))}",
)

for dx in cd.get("diagnoses", []):
    check(
        f"Diagnosis '{dx.get('description')}' has required fields",
        all(k in dx for k in ("description", "icd_code", "confidence")),
    )

original_med_count = len(test_input["clinical_data"]["medications_prescribed"])
total_med_count = len(cd.get("medications_prescribed", []))
check(
    "Medications were augmented",
    total_med_count >= original_med_count,
    f"original={original_med_count}, total={total_med_count}",
)

for med in cd.get("medications_prescribed", []):
    check(
        f"Medication '{med.get('name')}' has name & frequency",
        "name" in med and "frequency" in med,
    )
    check(
        f"Medication '{med.get('name')}' frequency is 'once daily'",
        med.get("frequency") == "once daily",
    )
print()

# ── Test 2: Assembled JSON passes validator ──────────────────────────────────
print("=== Test 2: Validate assembled JSON ===")
result = validate_and_normalize(assembled)
check("Validation passes", result["valid"], f"errors={result['errors']}")
check("No errors", len(result["errors"]) == 0)
print(f"  Warnings: {result['warnings']}")
print()

# ── Test 3: Assembled JSON works through post-processor ──────────────────────
print("=== Test 3: Post-process with fake LLM response ===")
normalized = result["normalized"]

fake_llm_response = {
    "greeting": f"Hi {normalized['patient']['name'].split()[0]}! Thank you for coming in today.",
    "what_we_found": "We found some conditions based on your symptoms.",
    "your_vitals": "Your blood pressure was 142/88, heart rate 94, temperature 98.6°F, and oxygen level 96%.",
    "your_medications": "Please take all medications once daily as prescribed.",
    "watch_for": "Watch for any worsening symptoms.",
    "next_steps": normalized["clinical_data"].get("follow_up", "Follow up with your doctor."),
    "closing": "Take care!",
}

processed = post_process(fake_llm_response, normalized["patient"]["name"])
check("Post-process returns summary", "summary" in processed)
check("Post-process returns html", "html" in processed)
check("Post-process returns meta", "meta" in processed)
check(
    "Word count is reasonable",
    processed["meta"]["word_count"] < 400,
    f"word_count={processed['meta']['word_count']}",
)
print()

# ── Test 4: Assembled JSON matches mock_patient.json schema exactly ──────────
print("=== Test 4: Schema matches mock_patient.json ===")
with open(MOCK_PATIENT_PATH) as f:
    mock = json.load(f)


def schema_keys(obj, prefix=""):
    """Recursively collect all key paths."""
    keys = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            path = f"{prefix}.{k}" if prefix else k
            keys.add(path)
            keys |= schema_keys(v, path)
    elif isinstance(obj, list) and obj:
        keys |= schema_keys(obj[0], prefix + "[0]")
    return keys


mock_schema = schema_keys(mock)
assembled_schema = schema_keys(assembled)

check(
    "All mock_patient.json keys present in assembled output",
    mock_schema.issubset(assembled_schema),
    f"missing={mock_schema - assembled_schema}",
)
print()

# ── Summary ──────────────────────────────────────────────────────────────────
print("=" * 50)
total = passed + failed
print(f"{passed}/{total} checks passed, {failed} failed")
if failed:
    print("SOME CHECKS FAILED — see above")
    sys.exit(1)
else:
    print("ALL CHECKS PASSED")
