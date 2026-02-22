/** Shared types for the consultation recording flow. */

export interface TranscriptEntry {
  speaker: 'doctor' | 'patient';
  text: string;
  timestamp: number; // seconds into recording
}

export interface Diagnosis {
  name: string;
  icdCode?: string;
  notes?: string;
}

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  notes?: string;         // e.g. "take with food", "new prescription"
  isNew?: boolean;        // newly prescribed in this visit
}

export interface FollowUp {
  description: string;
  date?: string;          // e.g. "2026-03-21" or "in 4 weeks"
  provider?: string;      // e.g. "Dr. Smith" or "Endocrinologist"
}

export interface LabTest {
  name: string;
  status: 'ordered' | 'completed' | 'pending';
  result?: string;        // e.g. "9.2%" for HbA1c
  date?: string;
  notes?: string;
}

export interface VisitSummary {
  visitDate: string;
  chiefComplaint: string;
  summaryText: string;    // plain-language summary of the visit
  diagnoses: Diagnosis[];
  medications: Medication[];
  followUps: FollowUp[];
  labTests: LabTest[];
  transcript: TranscriptEntry[];
}

/** Legacy types kept for API compatibility */
export interface TaggedEntity {
  type: 'disease' | 'symptom' | 'medication' | 'procedure';
  value: string;
  confidence: number;
}

export interface ConsultationSummary {
  chiefComplaint: string;
  summaryText: string;
  tags: TaggedEntity[];
  transcript: TranscriptEntry[];
}

export interface MedicationRecommendation {
  name: string;
  icdCode: string;
  icdDescription: string;
  fdaReportCount: number;
  rank: number;
}

export interface ConsultationResult {
  id: string;
  visit: VisitSummary;
}
