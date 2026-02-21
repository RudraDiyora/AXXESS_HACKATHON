import pytesseract
import os
import platform
import sys
import io
from PIL import Image, ImageEnhance
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

app = FastAPI()


def _configure_tesseract():
    """Auto-detect OS and set the Tesseract binary path."""
    system = platform.system()
    if system == "Windows":
        win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(win_path):
            pytesseract.pytesseract.tesseract_cmd = win_path
        # else: hope it's on PATH
    # macOS / Linux: tesseract is expected on PATH via brew or apt

_configure_tesseract()


def extract_text_from_image(image: Image.Image) -> str:
    """
    Pre-process a PIL Image for OCR and return the extracted text.
    Works regardless of how the image was obtained (file, upload, camera).
    """
    img = image.convert("L")

    # Enhance contrast
    img = ImageEnhance.Contrast(img).enhance(1.5)
    # Enhance sharpness
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    # Binarise: pixels darker than 100 → black, rest → white
    img = img.point(lambda x: 0 if x < 100 else 255, "1")

    text = pytesseract.image_to_string(img)
    return text.strip()


# ---------------------------------------------------------------------------
# FastAPI endpoint — phone / any HTTP client sends an image here
# ---------------------------------------------------------------------------

@app.post("/extract-text/")
async def extract_text_endpoint(file: UploadFile = File(...)):
    """
    Accept an uploaded image (jpg, png, etc.), run OCR, and return the text.
    A phone camera app or frontend can POST to this endpoint.
    """
    allowed_types = {"image/jpeg", "image/png", "image/tiff", "image/bmp", "image/webp"}
    if file.content_type and file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported image type: {file.content_type}. Accepted: {', '.join(allowed_types)}",
        )

    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read the uploaded file as an image.")

    try:
        text = extract_text_from_image(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR failed: {e}")

    return JSONResponse(content={"filename": file.filename, "extracted_text": text})


# ---------------------------------------------------------------------------
# CLI fallback — still works from the terminal for local testing
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = input("Enter the path to the image file: ")

    if not os.path.exists(image_path):
        print("File not found.")
        sys.exit(1)

    img = Image.open(image_path)
    text = extract_text_from_image(img)
    print("\n--- Extracted Text ---")
    print(text)
    