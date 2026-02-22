"""
Pydantic models for request/response schemas across all pipeline stages.
"""

from datetime import date
from pydantic import BaseModel, Field


# ── Patient & Visit ─────────────────────────────────────────────────────────

class PatientInfo(BaseModel):
    name: str = Field(default="Unknown", description="Patient full name")
    age: int | None = Field(default=None, description="Patient age")
    preferred_language: str = Field(default="en", description="Preferred language code")


class VisitInfo(BaseModel):
    date: str = Field(default_factory=lambda: date.today().isoformat())
    type: str = Field(default="consultation")
    clinician: str = Field(default="Your care team")


# ── Clinical Data (from extraction) ────────────────────────────────────────

class Vitals(BaseModel):
    bp: str = Field(default="N/A", description="Blood pressure, e.g. '120/80'")
    hr: int | None = Field(default=None, description="Heart rate in bpm")
    temp: float | None = Field(default=None, description="Temperature in °F")
    o2_sat: int | None = Field(default=None, description="Oxygen saturation %")


class Diagnosis(BaseModel):
    description: str = Field(description="Diagnosis or condition name")
    icd_code: str = Field(default="", description="ICD-10 code if applicable")
    confidence: float = Field(default=0.0, description="Confidence score 0-1")


class MedicationPrescribed(BaseModel):
    name: str = Field(description="Medication name")
    dose: str = Field(default="", description="Dosage amount, e.g. '10mg'")
    frequency: str = Field(description="Dosage frequency, e.g. 'once daily'")
    purpose: str = Field(default="", description="Reason for prescribing")


class ClinicalData(BaseModel):
    chief_complaint: str = Field(description="Primary reason for the visit")
    vitals: Vitals = Field(default_factory=Vitals)
    symptoms: list[str] = Field(default_factory=list, description="Symptoms mentioned")
    diagnoses: list[Diagnosis] = Field(default_factory=list)
    medications_prescribed: list[MedicationPrescribed] = Field(default_factory=list)
    follow_up: str = Field(default="N/A", description="Follow-up instructions")


# ── Transcript (from speech-to-text) ───────────────────────────────────────

class TranscriptMessage(BaseModel):
    speaker: str
    text: str


class TranscriptInput(BaseModel):
    session_id: str = Field(default="unknown_session")
    patient: PatientInfo = Field(default_factory=PatientInfo)
    messages: list[TranscriptMessage] = Field(default_factory=list)


# ── Full clinical input (for summary generation) ──────────────────────────

class SummaryInput(BaseModel):
    patient: PatientInfo
    visit: VisitInfo = Field(default_factory=VisitInfo)
    clinical_data: ClinicalData


# ── Pipeline request ──────────────────────────────────────────────────────

class PipelinePatientInfo(BaseModel):
    name: str = Field(default="John Doe")
    age: int = Field(default=30)
    gender: str = Field(default="unknown")


# ── Response models ───────────────────────────────────────────────────────

class SummaryResponse(BaseModel):
    greeting: str = ""
    what_we_found: str = ""
    your_vitals: str = ""
    your_medications: str = ""
    watch_for: str = ""
    next_steps: str = ""
    closing: str = ""


class SummaryMeta(BaseModel):
    word_count: int
    too_long: bool
    flagged: list[str] = Field(default_factory=list)
