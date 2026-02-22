import React, { createContext, useContext, useState, useCallback } from 'react';
import type { VisitRecord } from '@/data/visits';

import rawData from '@/data.json';

interface PatientInfo {
  name: string;
  age: number;
  preferred_language: string;
  phone: string;
}

interface CaregiverInfo {
  name: string;
  relationship: string;
  phone: string;
  email: string;
}

interface DataContextValue {
  patient: PatientInfo;
  caregiver: CaregiverInfo | null;
  setCaregiver: (c: CaregiverInfo | null) => void;
  visits: VisitRecord[];
  addVisit: (visit: VisitRecord) => void;
}

const DataContext = createContext<DataContextValue>({
  patient: rawData.patient as PatientInfo,
  caregiver: rawData.caregiver as CaregiverInfo,
  setCaregiver: () => {},
  visits: [],
  addVisit: () => {},
});

export function DataProvider({ children }: { children: React.ReactNode }) {
  const [patient] = useState<PatientInfo>(rawData.patient as PatientInfo);
  const [caregiver, setCaregiver] = useState<CaregiverInfo | null>(
    rawData.caregiver as CaregiverInfo
  );
  const [visits, setVisits] = useState<VisitRecord[]>(rawData.visits as VisitRecord[]);

  const addVisit = useCallback((visit: VisitRecord) => {
    setVisits((prev) => [visit, ...prev]);
  }, []);

  return (
    <DataContext.Provider value={{ patient, caregiver, setCaregiver, visits, addVisit }}>
      {children}
    </DataContext.Provider>
  );
}

export function useAppData() {
  return useContext(DataContext);
}
