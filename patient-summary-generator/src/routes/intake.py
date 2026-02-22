"""Intake route — accepts partial patient JSON (no diagnoses),
assembles a complete record, and runs the full summary pipeline.
"""

from flask import Blueprint, request, jsonify

from src.services.patient_assembler import assemble_patient_json
from src.services.validator import validate_and_normalize
from src.services.llm_service import generate_summary
from src.services.post_processor import post_process

intake_bp = Blueprint("intake", __name__)


@intake_bp.route("/process", methods=["POST"])
def process_intake():
    """Accept partial patient JSON → assemble → summarise → return."""
    try:
        data = request.get_json(force=True)

        # 1. Assemble (diagnoses + medication enrichment)
        assembled = assemble_patient_json(data)

        # 2. Validate
        result = validate_and_normalize(assembled)
        if not result["valid"]:
            return jsonify({"success": False, "errors": result["errors"]}), 400

        normalized = result["normalized"]

        # 3. LLM summary
        raw_summary = generate_summary(normalized)

        # 4. Post-process
        processed = post_process(raw_summary, normalized["patient"]["name"])

        return jsonify({
            "success": True,
            "warnings": result["warnings"],
            "assembled_data": assembled,
            **processed,
        }), 200

    except Exception as e:
        print(f"Intake error: {e}")
        return jsonify({"success": False, "error": "Intake processing failed"}), 500
