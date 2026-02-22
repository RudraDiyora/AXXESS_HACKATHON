"""Patient JSON Assembler

Takes an incoming patient JSON that has everything EXCEPT diagnoses
(and potentially only some medications), calls the ICD-10 / medication
lookup APIs to generate diagnoses and discover additional medications,
then outputs a complete JSON in the exact format of mock_patient.json
so downstream services (validator → LLM → post-processor) work unchanged.

All discovered medications are assumed to be taken once daily.
"""

import json
import re
from typing import Any

from src.routes.icd_code_medications import (
    get_medications_for_disease,
    search_icd10_code,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _extract_search_terms(clinical_data: dict) -> list[str]:
    """Build a list of search terms from the chief complaint and symptoms.

    Strategy:
    1. Use each individual symptom as a search term.
    2. Split the chief complaint into meaningful phrases by punctuation /
       conjunctions and use each fragment as a search term.
    3. De-duplicate while preserving order.
    """
    terms: list[str] = []

    # Symptoms are usually terse clinical phrases — perfect search terms.
    for symptom in clinical_data.get("symptoms", []):
        clean = symptom.strip()
        if clean and clean not in terms:
            terms.append(clean)

    # Chief complaint may be a sentence — split on "and", commas, "for", "with".
    cc = clinical_data.get("chief_complaint", "")
    if cc:
        fragments = re.split(r"\band\b|,|\bfor\b|\bwith\b", cc, flags=re.IGNORECASE)
        for frag in fragments:
            clean = frag.strip().rstrip(".")
            # Skip very short fragments (numbers, durations like "3 days")
            if clean and len(clean) > 4 and not re.match(r"^\d+\s*(days?|weeks?|months?)$", clean, re.IGNORECASE):
                if clean not in terms:
                    terms.append(clean)

    return terms


def _normalise_drug_name(name: str) -> str:
    """Lowercase base drug name for de-duplication.

    Strips dosage info, salt forms, and common suffixes so that
    'Albuterol Sulfate' and 'Albuterol' both become 'albuterol'.
    """
    base = name.lower()
    # Remove dosage patterns like "500 mg"
    base = re.split(r"\s+\d+\s*m?g", base)[0].strip()
    # Remove common salt/form suffixes
    base = re.sub(
        r"\s+(sulfate|hcl|hydrochloride|sodium|potassium|er|xr|sr|cr|la|xl)$",
        "",
        base,
    ).strip()
    return base


# ---------------------------------------------------------------------------
# Main assembler
# ---------------------------------------------------------------------------

def assemble_patient_json(input_data: dict) -> dict:
    """Accept a partial patient JSON (no diagnoses) and return a complete one.

    Parameters
    ----------
    input_data : dict
        Must contain ``patient`` and ``clinical_data`` keys.
        ``clinical_data`` must NOT contain ``diagnoses`` (or it will be
        ignored and regenerated).
        ``clinical_data.medications_prescribed`` may be partially filled.

    Returns
    -------
    dict
        A JSON-serialisable dict matching the ``mock_patient.json`` schema
        with generated ``diagnoses`` and augmented ``medications_prescribed``.
    """
    patient = input_data.get("patient", {})
    clinical = input_data.get("clinical_data", {})

    # Existing medications from the input --------------------------------
    existing_meds: list[dict] = list(clinical.get("medications_prescribed", []))
    existing_med_names = {_normalise_drug_name(m["name"]) for m in existing_meds}

    # Derived search terms -----------------------------------------------
    search_terms = _extract_search_terms(clinical)
    if not search_terms:
        # Fallback: use the raw chief complaint
        cc = clinical.get("chief_complaint", "")
        if cc:
            search_terms = [cc]

    # Lookup diagnoses & medications -------------------------------------
    diagnoses: list[dict] = []
    new_meds: list[dict] = []
    seen_icd_codes: set[str] = set()

    for term in search_terms:
        result = search_icd10_code(term)
        if result is None:
            continue

        icd_code, icd_name = result

        # Avoid duplicate diagnosis entries
        if icd_code in seen_icd_codes:
            continue
        seen_icd_codes.add(icd_code)

        diagnoses.append({
            "description": icd_name,
            "icd_code": icd_code,
            "confidence": 0.91,  # default high-confidence
        })

        # Fetch medications for this condition
        _, medications = get_medications_for_disease(term, top_n=5)
        for med_name, _count in medications:
            base = _normalise_drug_name(med_name)
            # Skip overly generic / non-pharmaceutical names
            if len(base) < 3 or " " in base or "-" in base:
                continue
            if base not in existing_med_names:
                existing_med_names.add(base)
                new_meds.append({
                    "name": med_name.title(),
                    "frequency": "once daily",
                })

    # Merge medications ---------------------------------------------------
    all_meds = existing_meds + new_meds

    # Build the full output JSON ------------------------------------------
    assembled: dict[str, Any] = {
        "patient": {
            "name": patient.get("name", "Patient"),
            "age": patient.get("age"),
            "preferred_language": patient.get("preferred_language", "en"),
        },
        "clinical_data": {
            "chief_complaint": clinical.get("chief_complaint"),
            "vitals": clinical.get("vitals", {}),
            "symptoms": clinical.get("symptoms", []),
            "diagnoses": diagnoses,
            "medications_prescribed": all_meds,
            "follow_up": clinical.get("follow_up"),
        },
    }

    return assembled


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    import sys

    # Default to the bundled test input
    input_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(__file__), "..", "data", "test_input.json",
    )
    input_path = os.path.abspath(input_path)

    with open(input_path) as fh:
        raw = json.load(fh)

    print(f"Reading input from: {input_path}\n")
    result = assemble_patient_json(raw)
    print(json.dumps(result, indent=2))
