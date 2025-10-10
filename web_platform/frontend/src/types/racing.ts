// web_platform/frontend/src/types/racing.ts
// This file is the central source of truth for frontend racing data types.

// --- Runner & Odds Interfaces ---
export interface OddsData {
  win: number | null;
  source: string;
  last_updated: string;
}

export interface Runner {
  number: number;
  name: string;
  scratched: boolean;
  selection_id?: number;
  odds: Record<string, OddsData>;
  jockey?: string;
  trainer?: string;
}

// --- Race Interface ---
// This interface matches the shape of the data returned by the API for the dashboard.
export interface Race {
  id: string;
  venue: string;
  race_number: number;
  start_time: string;
  runners: Runner[];
  source: string;
  qualification_score?: number;
  distance?: string;
  surface?: string;
}

// --- Analysis Factor Interfaces (retained from previous version) ---
export interface Factor {
    points: number;
    ok: boolean;
    reason: string;
}

export interface TrifectaFactors {
    [key: string]: Factor;
}