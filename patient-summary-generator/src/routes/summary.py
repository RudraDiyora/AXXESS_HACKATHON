from flask import Blueprint, request, jsonify

from src.services.validator import validate_and_normalize
from src.services.llm_service import generate_summary
from src.services.post_processor import post_process

summary_bp = Blueprint("summary", __name__)


@summary_bp.route("/generate", methods=["POST"])
def generate():
    try:
        data = request.get_json(force=True)
        result = validate_and_normalize(data)

        if not result["valid"]:
            return jsonify({"success": False, "errors": result["errors"]}), 400

        normalized = result["normalized"]
        raw_summary = generate_summary(normalized)
        processed = post_process(raw_summary, normalized["patient"]["name"])

        return jsonify({
            "success": True,
            "warnings": result["warnings"],
            **processed,
        }), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": "Summary generation failed"}), 500
