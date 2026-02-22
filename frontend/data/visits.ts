import type { Diagnosis, Medication, FollowUp, LabTest, TranscriptEntry } from '@/types/consultation';

import rawData from '@/data.json';

export interface VisitRecord {
  id: string;
  doctorName: string;
  specialty: string;
  visitDate: string;
  chiefComplaint: string;
  summaryText: string;
  vitals?: {
    bp?: string;
    hr?: number;
    temp?: number;
    o2_sat?: number;
  };
  symptoms?: string[];
  diagnoses: Diagnosis[];
  medications: Medication[];
  followUps: FollowUp[];
  labTests: LabTest[];
  transcript: TranscriptEntry[];
}

// Mutable array loaded from data.json — the DataProvider is the real source of truth,
// but these module-level helpers still work for non-context consumers.
let visits: VisitRecord[] = rawData.visits as VisitRecord[];

/** Replace the in-memory visits array (called by DataProvider sync). */
export function _setVisits(v: VisitRecord[]) {
  visits = v;
}

export function getVisits(): VisitRecord[] {
  return visits;
}

export function getVisit(id: string): VisitRecord | undefined {
  return visits.find((v) => v.id === id);
}

/** Aggregate active medications from latest visits (latest version wins) */
export function getCurrentMedications(): (Medication & { fromVisit: string })[] {
  const medMap = new Map<string, Medication & { fromVisit: string }>();
  const sorted = [...visits].reverse();
  for (const visit of sorted) {
    for (const med of visit.medications) {
      medMap.set(med.name.toLowerCase(), { ...med, fromVisit: visit.visitDate });
    }
  }
  return Array.from(medMap.values());
}

/** Get upcoming/future follow-ups across all visits */
export function getUpcomingAppointments(): (FollowUp & { fromVisit: string })[] {
  const all: (FollowUp & { fromVisit: string })[] = [];
  for (const visit of visits) {
    for (const fu of visit.followUps) {
      all.push({ ...fu, fromVisit: visit.visitDate });
    }
  }
  return all;
}

/** Get pending/ordered lab tests across all visits */
export function getPendingLabs(): (LabTest & { fromVisit: string })[] {
  const all: (LabTest & { fromVisit: string })[] = [];
  for (const visit of visits) {
    for (const lab of visit.labTests) {
      if (lab.status !== 'completed') {
        all.push({ ...lab, fromVisit: visit.visitDate });
      }
    }
  }
  return all;
}

/** Add a new visit to the in-memory store */
export function addVisitToStore(visit: VisitRecord) {
  visits = [visit, ...visits];
}

