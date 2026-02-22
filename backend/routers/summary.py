"""
Patient summary generation endpoints — takes clinical data and produces
a patient-friendly summary with HTML rendering.

Source: Patient_Summary_Generator branch
"""

import json

from fastapi import APIRouter, HTTPException, Request

from services.validator import validate_and_normalize
from services.summary_service import generate_summary
from services.post_processor import post_process

router = APIRouter(prefix="/api/summary", tags=["Patient Summary"])


@router.post("/generate")
async def generate(request: Request):
    """
    Accept structured clinical data and generate a patient-friendly
    visit summary. Returns JSON summary, HTML rendering, and metadata.
    """
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON body.")

    result = validate_and_normalize(data)

    if not result["valid"]:
        raise HTTPException(
            status_code=400,
            detail={"errors": result["errors"]},
        )

    try:
        normalized = result["normalized"]
        raw_summary = generate_summary(normalized)
        processed = post_process(raw_summary, normalized["patient"]["name"])

        return {
            "success": True,
            "warnings": result["warnings"],
            **processed,
        }

    except Exception as e:
        print(f"Summary generation error: {e}")
        raise HTTPException(
            status_code=500,
            detail="Summary generation failed.",
        )
