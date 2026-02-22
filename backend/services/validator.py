"""
Input validation and normalisation.

Source: Patient_Summary_Generator branch (src/services/validator.py)
"""

from datetime import date


def validate_and_normalize(data: dict) -> dict:
    """
    Validate incoming clinical data and return a normalised version.

    Returns a dict with keys: normalized, errors, warnings, valid.
    """
    errors: list[str] = []
    warnings: list[str] = []

    patient = data.get("patient") or {}
    clinical_data = data.get("clinical_data")
    visit = data.get("visit") or {}

    if not patient.get("name"):
        errors.append("Missing patient name")
    if clinical_data is None:
        errors.append("Missing clinical data entirely")

    cd = clinical_data or {}
    if not cd.get("diagnoses"):
        warnings.append("No diagnoses provided")
    if not cd.get("medications_prescribed"):
        warnings.append("No medications provided")

    normalized = {
        "patient": {
            "name": patient.get("name", "Patient"),
            "age": patient.get("age"),
            "preferred_language": patient.get("preferred_language", "en"),
        },
        "visit": {
            "date": visit.get("date", date.today().isoformat()),
            "type": visit.get("type", "visit"),
            "clinician": visit.get("clinician", "Your care team"),
        },
        "clinical_data": {
            "chief_complaint": cd.get("chief_complaint"),
            "vitals": cd.get("vitals", {}),
            "symptoms": cd.get("symptoms", []),
            "diagnoses": cd.get("diagnoses", []),
            "medications_prescribed": cd.get("medications_prescribed", []),
            "follow_up": cd.get("follow_up"),
        },
    }

    return {
        "normalized": normalized,
        "errors": errors,
        "warnings": warnings,
        "valid": len(errors) == 0,
    }
