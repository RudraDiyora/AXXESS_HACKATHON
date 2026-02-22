"""
Image OCR service — extract text from uploaded images using Tesseract.

Source: Jaideep's-Branch (img_to_text.py)
"""

import io
import os
import platform

import pytesseract
from PIL import Image, ImageEnhance


def _configure_tesseract():
    """Auto-detect OS and set the Tesseract binary path."""
    system = platform.system()
    if system == "Windows":
        win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(win_path):
            pytesseract.pytesseract.tesseract_cmd = win_path


_configure_tesseract()


def extract_text_from_image(image: Image.Image) -> str:
    """
    Pre-process a PIL Image for OCR and return the extracted text.
    Works regardless of how the image was obtained (file, upload, camera).
    """
    img = image.convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Sharpness(img).enhance(1.2)
    img = img.point(lambda x: 0 if x < 100 else 255, "1")

    text = pytesseract.image_to_string(img)
    return text.strip()


def extract_text_from_bytes(image_bytes: bytes) -> str:
    """Convenience wrapper: bytes → PIL Image → OCR text."""
    image = Image.open(io.BytesIO(image_bytes))
    return extract_text_from_image(image)
