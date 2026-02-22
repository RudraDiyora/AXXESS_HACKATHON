# Medical Visit Pipeline — Backend API

Unified FastAPI backend combining speech-to-text transcription, clinical data extraction, image OCR, and patient-friendly summary generation.

## Architecture

```
Audio File ──► Speech-to-Text (AssemblyAI) ──► Transcript JSON
                                                    │
                                                    ▼
Image File ──► OCR (Tesseract) ──►          Clinical Extraction (LLM)
                                                    │
                                                    ▼
                                          Patient Summary (LLM)
                                                    │
                                                    ▼
                                          Post-Processing (jargon → plain English)
                                                    │
                                                    ▼
                                          HTML + JSON Output
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/speech-to-text/transcribe` | Upload audio → structured Doctor/Patient transcript |
| `POST` | `/api/ocr/extract-text` | Upload image → extracted text via Tesseract OCR |
| `POST` | `/api/extract/from-transcript` | Transcript JSON file → clinical data (diagnoses, ICD codes, meds) |
| `POST` | `/api/extract/from-json` | Transcript JSON body → clinical data |
| `POST` | `/api/summary/generate` | Clinical data → patient-friendly summary + HTML |
| `POST` | `/api/pipeline/run` | Full pipeline: audio → transcript → extraction → summary |
| `POST` | `/api/pipeline/run-from-transcript` | Pipeline from existing transcript (skip audio) |
| `GET`  | `/docs` | Interactive Swagger UI |
| `GET`  | `/health` | Health check |

## Setup

```bash
cd backend
pip install -r requirements.txt

# Copy .env and set your API keys
cp .env.example .env
```

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `FEATHERLESS_API_KEY` | API key for Featherless AI (LLM calls) |
| `FEATHERLESS_MODEL` | Model name (default: `deepseek-ai/DeepSeek-V3-0324`) |
| `ASSEMBLYAI_API_KEY` | API key for AssemblyAI (speech-to-text) |

## Running

```bash
cd backend
python app.py
# or
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

API docs available at `http://localhost:8000/docs`

## Testing

```bash
# Offline tests (no API keys needed)
python tests/test_offline.py

# Live pipeline test (requires FEATHERLESS_API_KEY)
python tests/test_live_pipeline.py
```

## Project Structure

```
backend/
├── app.py                          # FastAPI entry point
├── config.py                       # Environment config
├── requirements.txt
├── .env
├── routers/
│   ├── speech_to_text.py           # Audio transcription endpoints
│   ├── ocr.py                      # Image OCR endpoints
│   ├── extraction.py               # Clinical data extraction endpoints
│   ├── summary.py                  # Summary generation endpoints
│   └── pipeline.py                 # Full pipeline endpoints
├── services/
│   ├── assembly_service.py         # AssemblyAI integration
│   ├── ocr_service.py              # Tesseract OCR
│   ├── extraction_service.py       # Transcript parsing + LLM extraction
│   ├── summary_service.py          # Patient summary LLM
│   ├── post_processor.py           # Jargon replacement + HTML rendering
│   └── validator.py                # Input validation
├── models/
│   └── schemas.py                  # Pydantic models
├── data/
│   ├── jargon_list.py              # Medical jargon → plain English
│   ├── mock_patient.json           # Test data
│   └── test_transcript.json        # Test transcript
├── prompts/
│   └── system_prompt.py            # LLM system prompts
└── tests/
    ├── test_offline.py             # Offline validator/processor tests
    └── test_live_pipeline.py       # End-to-end LLM test
```

## Sources

- **Speech-to-Text**: `speech_to_text_WORKING` branch — AssemblyAI transcription with speaker diarization
- **Clinical Extraction**: `Jaideep's-Branch` — LLM-based medical data extraction, OCR
- **Patient Summary**: `Patient_Summary_Generator` branch — Summary generation, jargon replacement, HTML rendering
