"""
Unified Backend API
===================
Combines all pipeline stages into a single FastAPI application:

  • /api/speech-to-text  — Upload audio → transcribed Doctor/Patient JSON
  • /api/ocr             — Upload image → extracted text via Tesseract
  • /api/extract         — Transcript JSON → clinical data (diagnoses, ICD codes, meds)
  • /api/summary         — Clinical data → patient-friendly summary + HTML
  • /api/pipeline        — Full end-to-end: audio → transcript → extraction → summary

Sources:
  - speech_to_text_WORKING  (AssemblyAI transcription, speaker diarization)
  - Jaideep's-Branch        (text extraction, LLM clinical extraction, OCR)
  - Patient_Summary_Generator (summary LLM, jargon replacement, HTML rendering)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import speech_to_text, ocr, extraction, summary, pipeline

app = FastAPI(
    title="Medical Visit Pipeline API",
    description=(
        "End-to-end pipeline: Audio transcription → Clinical data extraction "
        "→ Patient-friendly summary generation"
    ),
    version="1.0.0",
)

# CORS — allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register routers ────────────────────────────────────────────────────────
app.include_router(speech_to_text.router)
app.include_router(ocr.router)
app.include_router(extraction.router)
app.include_router(summary.router)
app.include_router(pipeline.router)


@app.get("/")
async def root():
    return {
        "service": "Medical Visit Pipeline API",
        "version": "1.0.0",
        "endpoints": {
            "speech_to_text": "POST /api/speech-to-text/transcribe",
            "ocr": "POST /api/ocr/extract-text",
            "extract": "POST /api/extract/from-transcript",
            "summary": "POST /api/summary/generate",
            "pipeline_full": "POST /api/pipeline/run",
            "pipeline_from_transcript": "POST /api/pipeline/run-from-transcript",
            "docs": "GET /docs",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("  Medical Visit Pipeline API")
    print("  http://0.0.0.0:8000")
    print("  Docs: http://0.0.0.0:8000/docs")
    print("=" * 60)
    uvicorn.run(app, host="0.0.0.0", port=8000)
