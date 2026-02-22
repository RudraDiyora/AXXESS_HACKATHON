/**
 * API client stub for the FastAPI backend.
 *
 * Replace BASE_URL with your actual backend URL.
 * All methods return typed data matching the consultation types.
 * The actual STT / NLP / recommendation logic lives in your backend —
 * this file only handles HTTP calls.
 */

import type { VisitSummary } from '@/types/consultation';

const BASE_URL = 'http://localhost:8000'; // ← swap with your FastAPI URL

/** Upload recorded audio for transcription + analysis. */
export async function uploadRecording(audioUri: string): Promise<{ visitId: string }> {
  const form = new FormData();
  form.append('audio', {
    uri: audioUri,
    type: 'audio/wav',
    name: 'recording.wav',
  } as any);

  const res = await fetch(`${BASE_URL}/visits/upload`, {
    method: 'POST',
    body: form,
  });

  if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
  return res.json();
}

/** Fetch the full visit summary (diagnoses, meds, follow-ups, labs). */
export async function fetchVisitSummary(visitId: string): Promise<VisitSummary> {
  const res = await fetch(`${BASE_URL}/visits/${visitId}/summary`);
  if (!res.ok) throw new Error(`Visit summary fetch failed: ${res.status}`);
  return res.json();
}
