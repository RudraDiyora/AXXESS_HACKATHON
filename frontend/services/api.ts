/**
 * API client for the FastAPI Medical Visit Pipeline backend.
 *
 * Endpoints:
 *   POST /api/pipeline/run                — Full pipeline: audio → transcript → extraction → summary
 *   POST /api/pipeline/run-from-transcript — Stages 2–3 from existing transcript
 *   POST /api/speech-to-text/transcribe   — Audio → structured transcript
 *   POST /api/extract/from-json           — Transcript → clinical data
 *   POST /api/summary/generate            — Clinical data → patient-friendly summary
 *   GET  /health                          — Health check
 */

import { Platform } from 'react-native';
import Constants from 'expo-constants';
import type { VisitRecord } from '@/data/visits';

// ── Backend URL ─────────────────────────────────────────────────────────────
// Auto-detect the dev server host so physical devices, emulators, and web all work.
// The Expo dev server's debuggerHost gives us "<IP>:<port>" — we swap the port to 8000.
function getBaseUrl(): string {
  const debuggerHost = Constants.expoConfig?.hostUri ?? Constants.manifest2?.extra?.expoGo?.debuggerHost;
  if (debuggerHost) {
    const host = debuggerHost.split(':')[0]; // strip Expo's port
    return `http://${host}:8000`;
  }
  // Fallback for Android emulator / web
  return Platform.select({
    android: 'http://10.0.2.2:8000',
    default: 'http://localhost:8000',
  })!;
}

const BASE_URL = getBaseUrl();

// ── Response Types ──────────────────────────────────────────────────────────

export interface PipelineResponse {
  status: string;
  stages: Record<string, any>;
  transcript: {
    session_id: string;
    patient: { name: string; age: number | null };
    messages: { speaker: string; text: string }[];
  };
  clinical_data: {
    patient: { name: string; age: number | null; preferred_language: string };
    visit: { date: string; type: string; clinician: string };
    clinical_data: {
      chief_complaint: string;
      vitals: { bp?: string; hr?: number; temp?: number; o2_sat?: number };
      symptoms: string[];
      diagnoses: { description: string; icd_code: string; confidence: number }[];
      medications_prescribed: { name: string; dose: string; frequency: string; purpose: string }[];
      follow_up: string;
    };
  };
  summary: {
    greeting: string;
    what_we_found: string;
    your_vitals: string;
    your_medications: string;
    watch_for: string;
    next_steps: string;
    closing: string;
  };
  html: string;
  meta: { word_count: number; too_long: boolean; flagged: string[] };
  warnings: string[];
}

// ── Health Check ────────────────────────────────────────────────────────────

/** Check if the backend is reachable. */
export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${BASE_URL}/health`, { method: 'GET' });
    return res.ok;
  } catch {
    return false;
  }
}

// ── Full Pipeline (audio → everything) ──────────────────────────────────────

/**
 * Run the full end-to-end pipeline:
 * 1. Upload audio → AssemblyAI transcription
 * 2. Extract clinical data via LLM
 * 3. Generate patient-friendly summary
 */
export async function runFullPipeline(
  audioUri: string,
  patientName: string = 'Unknown',
  patientAge?: number,
  sessionId: string = `session_${Date.now()}`,
): Promise<PipelineResponse> {
  const form = new FormData();

  // Determine file extension from URI
  const ext = audioUri.split('.').pop()?.toLowerCase() ?? 'wav';
  const mimeMap: Record<string, string> = {
    wav: 'audio/wav',
    mp3: 'audio/mpeg',
    m4a: 'audio/mp4',
    webm: 'audio/webm',
    ogg: 'audio/ogg',
    flac: 'audio/flac',
  };

  form.append('file', {
    uri: audioUri,
    type: mimeMap[ext] ?? 'application/octet-stream',
    name: `recording.${ext}`,
  } as any);

  form.append('session_id', sessionId);
  form.append('patient_name', patientName);
  if (patientAge != null) {
    form.append('patient_age', String(patientAge));
  }

  const res = await fetch(`${BASE_URL}/api/pipeline/run`, {
    method: 'POST',
    body: form,
    // Let React Native set the Content-Type with boundary for FormData
  });

  if (!res.ok) {
    const errBody = await res.text();
    throw new Error(`Pipeline failed (${res.status}): ${errBody}`);
  }

  return res.json();
}

// ── Pipeline from Transcript ────────────────────────────────────────────────

/** Run stages 2-3 from an existing transcript JSON (skip audio upload). */
export async function runPipelineFromTranscript(
  transcriptData: object,
): Promise<PipelineResponse> {
  const res = await fetch(`${BASE_URL}/api/pipeline/run-from-transcript`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transcriptData),
  });

  if (!res.ok) {
    const errBody = await res.text();
    throw new Error(`Pipeline failed (${res.status}): ${errBody}`);
  }

  return res.json();
}

// ── Speech-to-Text Only ─────────────────────────────────────────────────────

/** Upload audio and get a structured transcript back (no extraction/summary). */
export async function transcribeAudio(
  audioUri: string,
  patientName: string = 'Unknown',
  patientAge?: number,
) {
  const form = new FormData();
  const ext = audioUri.split('.').pop()?.toLowerCase() ?? 'wav';
  const mimeMap: Record<string, string> = {
    wav: 'audio/wav', mp3: 'audio/mpeg', m4a: 'audio/mp4',
    webm: 'audio/webm', ogg: 'audio/ogg', flac: 'audio/flac',
  };

  form.append('file', {
    uri: audioUri,
    type: mimeMap[ext] ?? 'application/octet-stream',
    name: `recording.${ext}`,
  } as any);

  const res = await fetch(
    `${BASE_URL}/api/speech-to-text/transcribe?session_id=session_${Date.now()}&patient_name=${encodeURIComponent(patientName)}${patientAge != null ? `&patient_age=${patientAge}` : ''}`,
    { method: 'POST', body: form },
  );

  if (!res.ok) {
    const errBody = await res.text();
    throw new Error(`Transcription failed (${res.status}): ${errBody}`);
  }

  return res.json();
}

// ── Clinical Extraction Only ────────────────────────────────────────────────

/** Extract clinical data from a transcript JSON body. */
export async function extractClinicalData(transcriptData: object) {
  const res = await fetch(`${BASE_URL}/api/extract/from-json`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(transcriptData),
  });

  if (!res.ok) {
    const errBody = await res.text();
    throw new Error(`Extraction failed (${res.status}): ${errBody}`);
  }

  return res.json();
}

// ── Summary Generation Only ─────────────────────────────────────────────────

/** Generate a patient-friendly summary from structured clinical data. */
export async function generateSummary(clinicalData: object) {
  const res = await fetch(`${BASE_URL}/api/summary/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(clinicalData),
  });

  if (!res.ok) {
    const errBody = await res.text();
    throw new Error(`Summary generation failed (${res.status}): ${errBody}`);
  }

  return res.json();
}

// ── Response → VisitRecord Transformer ──────────────────────────────────────

/**
 * Convert a backend PipelineResponse into the frontend VisitRecord format
 * used by the data layer and UI components.
 */
export function pipelineResponseToVisitRecord(response: PipelineResponse): VisitRecord {
  const cd = response.clinical_data?.clinical_data ?? {};
  const visit = response.clinical_data?.visit ?? {};
  const transcript = response.transcript ?? { messages: [] };
  const summary = response.summary ?? {};

  // Format visit date for display
  const rawDate = visit.date ?? new Date().toISOString().slice(0, 10);
  const visitDate = formatDateForDisplay(rawDate);

  // Build summary text from structured summary sections
  const summaryParts = [
    summary.what_we_found,
    summary.your_vitals,
    summary.your_medications,
    summary.watch_for,
    summary.next_steps,
  ].filter(Boolean);
  const summaryText = summaryParts.join(' ') || 'Visit summary is being processed.';

  // Map diagnoses: backend {description, icd_code} → frontend {name, icdCode, notes}
  const diagnoses = (cd.diagnoses ?? []).map((d: any) => ({
    name: d.description ?? d.name ?? 'Unknown',
    icdCode: d.icd_code ?? d.icdCode ?? '',
    notes: d.notes ?? '',
  }));

  // Map medications: backend {name, dose, frequency, purpose} → frontend {name, dosage, frequency, notes, isNew}
  const medications = (cd.medications_prescribed ?? []).map((m: any) => ({
    name: m.name ?? 'Unknown',
    dosage: m.dose ?? m.dosage ?? '',
    frequency: m.frequency ?? '',
    notes: m.purpose ?? m.notes ?? '',
    isNew: true, // all meds from a new visit are treated as new prescriptions
  }));

  // Parse follow_up string into structured follow-ups
  const followUps = parseFollowUps(cd.follow_up);

  // Map transcript messages: backend {speaker: "Doctor"/"Patient"} → frontend {speaker: "doctor"/"patient", timestamp}
  const transcriptEntries = (transcript.messages ?? []).map(
    (msg: { speaker: string; text: string }, index: number) => ({
      speaker: msg.speaker.toLowerCase().includes('doctor') ? ('doctor' as const) : ('patient' as const),
      text: msg.text.trim(),
      timestamp: index * 5, // approximate timestamps since backend doesn't provide exact ones
    }),
  );

  return {
    id: String(Date.now()),
    doctorName: visit.clinician ?? 'Your care team',
    specialty: visit.type === 'consultation' ? 'General Medicine' : (visit.type ?? 'Consultation'),
    visitDate,
    chiefComplaint: cd.chief_complaint ?? 'Visit recorded',
    summaryText,
    vitals: cd.vitals
      ? {
          bp: cd.vitals.bp ?? undefined,
          hr: cd.vitals.hr ?? undefined,
          temp: cd.vitals.temp ?? undefined,
          o2_sat: cd.vitals.o2_sat ?? undefined,
        }
      : undefined,
    symptoms: cd.symptoms ?? [],
    diagnoses,
    medications,
    followUps,
    labTests: [], // backend doesn't extract lab orders from transcripts currently
    transcript: transcriptEntries,
  };
}

/** Format an ISO date string (YYYY-MM-DD) into "Month Day, Year". */
function formatDateForDisplay(isoDate: string): string {
  try {
    const [year, month, day] = isoDate.split('-').map(Number);
    const date = new Date(year, month - 1, day);
    return date.toLocaleDateString('en-US', {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return isoDate;
  }
}

/** Parse a follow-up string into structured FollowUp objects. */
function parseFollowUps(followUp?: string): { description: string; date?: string; provider?: string }[] {
  if (!followUp || followUp === 'N/A') return [];
  // Split on common delimiters (semicolons, numbered lists)
  const parts = followUp
    .split(/[;\n]|(?:\d+\.\s)/)
    .map((s) => s.trim())
    .filter(Boolean);
  return parts.map((desc) => ({ description: desc }));
}
