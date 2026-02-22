"""
Image OCR endpoints — upload an image and extract text.

Source: Jaideep's-Branch (img_to_text.py)
"""

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from services.ocr_service import extract_text_from_bytes

router = APIRouter(prefix="/api/ocr", tags=["OCR"])

ALLOWED_TYPES = {
    "image/jpeg", "image/png", "image/tiff",
    "image/bmp", "image/webp",
}


@router.post("/extract-text")
async def extract_text_endpoint(file: UploadFile = File(...)):
    """
    Accept an uploaded image (jpg, png, etc.), run OCR, and return the
    extracted text.
    """
    if file.content_type and file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported image type: {file.content_type}. "
                f"Accepted: {', '.join(ALLOWED_TYPES)}"
            ),
        )

    try:
        contents = await file.read()
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Could not read the uploaded file.",
        )

    try:
        text = extract_text_from_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

    return JSONResponse(
        content={"filename": file.filename, "extracted_text": text}
    )
