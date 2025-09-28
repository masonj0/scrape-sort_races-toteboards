export interface FactorResult {
  points: number;
  ok: boolean;
  reason: string;
}

export interface Race {
  race_id: string;
  track_name: string;
  race_number: number | null;
  post_time: string;
  checkmate_score: number | null;
  is_qualified: boolean;
  trifecta_factors_json: string | null;
}