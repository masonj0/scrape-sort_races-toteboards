// lib.rs - Synthesized, production-grade Rust implementation of the Analysis Core

use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::panic;

// --- Data Structures for Serialization (JSON) ---

#[derive(Serialize, Deserialize, Debug)]
pub struct Runner {
    pub name: String,
    pub odds: Option<f64>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct RaceData {
    pub race_id: String,
    pub runners: Vec<Runner>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct AnalysisSettings {
    #[serde(rename = "QUALIFICATION_SCORE")]
    pub qualification_score: f64,
    #[serde(rename = "FIELD_SIZE_OPTIMAL_MIN")]
    pub field_size_optimal_min: usize,
    #[serde(rename = "FIELD_SIZE_OPTIMAL_MAX")]
    pub field_size_optimal_max: usize,
    #[serde(rename = "FIELD_SIZE_ACCEPTABLE_MIN")]
    pub field_size_acceptable_min: usize,
    #[serde(rename = "FIELD_SIZE_ACCEPTABLE_MAX")]
    pub field_size_acceptable_max: usize,
    #[serde(rename = "FIELD_SIZE_OPTIMAL_POINTS")]
    pub field_size_optimal_points: f64,
    #[serde(rename = "FIELD_SIZE_ACCEPTABLE_POINTS")]
    pub field_size_acceptable_points: f64,
    #[serde(rename = "FIELD_SIZE_PENALTY_POINTS")]
    pub field_size_penalty_points: f64,
    #[serde(rename = "FAV_ODDS_POINTS")]
    pub fav_odds_points: f64,
    #[serde(rename = "MAX_FAV_ODDS")]
    pub max_fav_odds: f64,
    #[serde(rename = "SECOND_FAV_ODDS_POINTS")]
    pub second_fav_odds_points: f64,
    #[serde(rename = "MIN_2ND_FAV_ODDS")]
    pub min_2nd_fav_odds: f64,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct RaceAnalysisRequest {
    pub races: Vec<RaceData>,
    pub settings: AnalysisSettings,
}

// --- Data Structures for Analysis Results ---

#[derive(Serialize, Deserialize, Debug)]
pub struct FactorResult {
    pub points: f64,
    pub ok: bool,
    pub reason: String,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct AnalysisResult {
    pub race_id: String,
    pub checkmate_score: f64,
    pub qualified: bool,
    pub trifecta_factors: HashMap<String, FactorResult>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct RaceAnalysisResponse {
    pub results: Vec<AnalysisResult>,
    pub processing_time_ms: u128,
}

// --- Core Analysis Logic ---

fn calculate_odds_spread(runners: &[&Runner]) -> f64 {
    if runners.len() < 2 { return 0.0; }
    let fav_odds = runners[0].odds.unwrap_or(1.0);
    let sec_fav_odds = runners[1].odds.unwrap_or(1.0);
    sec_fav_odds - fav_odds
}

fn analyze_odds_spread(spread: f64) -> f64 {
    // Example logic: A tight spread might indicate a competitive, unpredictable race.
    if spread < 1.5 { -10.0 }
    else if spread > 4.0 { 15.0 }
    else { 5.0 }
}

pub fn analyze_single_race_advanced(race: &RaceData, settings: &AnalysisSettings) -> AnalysisResult {
    let mut score = 0.0;
    let mut factors = HashMap::new();

    let mut horses_with_odds: Vec<&Runner> = race.runners.iter().filter(|r| r.odds.is_some()).collect();
    horses_with_odds.sort_by(|a, b| a.odds.unwrap().partial_cmp(&b.odds.unwrap()).unwrap());
    let num_runners = horses_with_odds.len();

    // Field Size Analysis
    let field_size_result = if (settings.field_size_optimal_min..=settings.field_size_optimal_max).contains(&num_runners) {
        FactorResult { points: settings.field_size_optimal_points, ok: true, reason: format!("Optimal field size ({})", num_runners) }
    } else if (settings.field_size_acceptable_min..=settings.field_size_acceptable_max).contains(&num_runners) {
        FactorResult { points: settings.field_size_acceptable_points, ok: true, reason: format!("Acceptable field size ({})", num_runners) }
    } else {
        FactorResult { points: settings.field_size_penalty_points, ok: false, reason: format!("Field size not ideal ({})", num_runners) }
    };
    score += field_size_result.points;
    factors.insert("fieldSize".to_string(), field_size_result);

    // Odds Analysis
    if num_runners >= 2 {
        let fav_odds = horses_with_odds[0].odds.unwrap();
        let sec_fav_odds = horses_with_odds[1].odds.unwrap();

        let fav_odds_result = if fav_odds <= settings.max_fav_odds {
            FactorResult { points: settings.fav_odds_points, ok: true, reason: format!("Favorite odds OK ({:.2})", fav_odds) }
        } else {
            FactorResult { points: 0.0, ok: false, reason: format!("Favorite odds too high ({:.2})", fav_odds) }
        };
        score += fav_odds_result.points;
        factors.insert("favoriteOdds".to_string(), fav_odds_result);

        let sec_fav_odds_result = if sec_fav_odds >= settings.min_2nd_fav_odds {
            FactorResult { points: settings.second_fav_odds_points, ok: true, reason: format!("2nd Favorite OK ({:.2})", sec_fav_odds) }
        } else {
            FactorResult { points: 0.0, ok: false, reason: format!("2nd Favorite odds too low ({:.2})", sec_fav_odds) }
        };
        score += sec_fav_odds_result.points;
        factors.insert("secondFavoriteOdds".to_string(), sec_fav_odds_result);

        // Odds Spread Analysis
        let odds_spread = calculate_odds_spread(&horses_with_odds);
        let spread_analysis_points = analyze_odds_spread(odds_spread);
        let odds_spread_result = FactorResult {
            points: spread_analysis_points,
            ok: spread_analysis_points >= 0.0, // Consider non-negative as OK
            reason: format!("Odds spread analysis ({:.2})", odds_spread),
        };
        score += odds_spread_result.points;
        factors.insert("oddsSpread".to_string(), odds_spread_result);
    }

    AnalysisResult {
        race_id: race.race_id.clone(),
        checkmate_score: score,
        qualified: score >= settings.qualification_score,
        trifecta_factors: factors,
    }
}

// --- FFI (Foreign Function Interface) for Python/C# ---

#[no_mangle]
pub extern "C" fn analyze_races_ffi_v2(input_json_ptr: *const c_char) -> *mut c_char {
    let result = panic::catch_unwind(|| {
        // 1. Safely read C string from pointer
        let input_c_str = unsafe { CStr::from_ptr(input_json_ptr) };
        let input_str = input_c_str.to_str().unwrap();

        // 2. Perform the analysis (your existing logic here)
        let request: RaceAnalysisRequest = serde_json::from_str(input_str).unwrap();
        let start_time = std::time::Instant::now();
        let results: Vec<_> = request.races.par_iter()
            .map(|race| analyze_single_race_advanced(race, &request.settings))
            .collect();
        let response = RaceAnalysisResponse {
            results,
            processing_time_ms: start_time.elapsed().as_millis(),
        };
        let response_json = serde_json::to_string(&response).unwrap();

        // 3. Safely return a C string pointer
        CString::new(response_json).unwrap().into_raw()
    });

    match result {
        Ok(json_ptr) => json_ptr,
        Err(_) => {
            // On panic, return a structured error JSON
            let error_json = r#"{"error": "A panic occurred in the Rust engine."}"#;
            CString::new(error_json).unwrap().into_raw()
        }
    }
}

#[no_mangle]
pub extern "C" fn free_string_ffi(s: *mut c_char) {
    if !s.is_null() {
        unsafe { CString::from_raw(s) };
    }
}