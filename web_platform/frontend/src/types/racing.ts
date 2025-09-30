// racing.ts - FINAL, EXPANDED VERSION

export interface Factor {
    points: number;
    ok: boolean;
    reason: string;
}

export interface TrifectaFactors {
    [key: string]: Factor;
}

export interface Race {
    race_id: string;
    track_name: string;
    race_number: number;
    post_time: string; // ISO 8601 string
    checkmate_score: number;
    qualified: boolean;
    trifecta_factors_json: string | null;
    raw_data_json: string | null;
    updated_at: string;
}