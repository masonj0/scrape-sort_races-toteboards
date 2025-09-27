// rust_engine/src/lib.rs
// The complete, production-grade Rust Analysis Core.

use rayon::prelude::*;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::ffi::{CStr, CString};
use std::os::raw::c_char;
use std::time::Instant;

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
#[allow(non_snake_case)] // Match Python model naming
pub struct AnalysisSettings {
    pub QUALIFICATION_SCORE: f64,
    pub FIELD_SIZE_OPTIMAL_MIN: usize,
    pub FIELD_SIZE_OPTIMAL_MAX: usize,
    pub FIELD_SIZE_ACCEPTABLE_MIN: usize,
    pub FIELD_SIZE_ACCEPTABLE_MAX: usize,
    pub FIELD_SIZE_OPTIMAL_POINTS: f64,
    pub FIELD_SIZE_ACCEPTABLE_POINTS: f64,
    pub FIELD_SIZE_PENALTY_POINTS: f64,
    pub FAV_ODDS_POINTS: f64,
    pub MAX_FAV_ODDS: f64,
    pub SECOND_FAV_ODDS_POINTS: f64,
    pub MIN_2ND_FAV_ODDS: f64,
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

pub fn analyze_races_parallel(request: RaceAnalysisRequest) -> RaceAnalysisResponse {
    let start_time = Instant::now();
    let settings = &request.settings;

    let results: Vec<AnalysisResult> = request
        .races
        .par_iter()
        .map(|race| {
            let mut score = 0.0;
            let mut factors = HashMap::new();

            let mut horses_with_odds: Vec<&Runner> =
                race.runners.iter().filter(|r| r.odds.is_some()).collect();
            horses_with_odds.sort_by(|a, b| a.odds.unwrap().partial_cmp(&b.odds.unwrap()).unwrap());
            let num_runners = horses_with_odds.len();

            // Field Size Analysis
            let field_size_result = if (settings.FIELD_SIZE_OPTIMAL_MIN..=settings.FIELD_SIZE_OPTIMAL_MAX).contains(&num_runners) {
                FactorResult { points: settings.FIELD_SIZE_OPTIMAL_POINTS, ok: true, reason: format!("Optimal field size ({})", num_runners) }
            } else if (settings.FIELD_SIZE_ACCEPTABLE_MIN..=settings.FIELD_SIZE_ACCEPTABLE_MAX).contains(&num_runners) {
                FactorResult { points: settings.FIELD_SIZE_ACCEPTABLE_POINTS, ok: true, reason: format!("Acceptable field size ({})", num_runners) }
            } else {
                FactorResult { points: settings.FIELD_SIZE_PENALTY_POINTS, ok: false, reason: format!("Field size not ideal ({})", num_runners) }
            };
            score += field_size_result.points;
            factors.insert("fieldSize".to_string(), field_size_result);

            // Favorite & Second Favorite Odds Analysis
            if num_runners >= 2 {
                let fav_odds = horses_with_odds[0].odds.unwrap();
                let sec_fav_odds = horses_with_odds[1].odds.unwrap();

                let fav_odds_result = if fav_odds <= settings.MAX_FAV_ODDS {
                    FactorResult { points: settings.FAV_ODDS_POINTS, ok: true, reason: format!("Favorite odds OK ({:.2})", fav_odds) }
                } else {
                    FactorResult { points: 0.0, ok: false, reason: format!("Favorite odds too high ({:.2})", fav_odds) }
                };
                score += fav_odds_result.points;
                factors.insert("favoriteOdds".to_string(), fav_odds_result);

                let sec_fav_odds_result = if sec_fav_odds >= settings.MIN_2ND_FAV_ODDS {
                    FactorResult { points: settings.SECOND_FAV_ODDS_POINTS, ok: true, reason: format!("2nd Favorite OK ({:.2})", sec_fav_odds) }
                } else {
                    FactorResult { points: 0.0, ok: false, reason: format!("2nd Favorite odds too low ({:.2})", sec_fav_odds) }
                };
                score += sec_fav_odds_result.points;
                factors.insert("secondFavoriteOdds".to_string(), sec_fav_odds_result);
            }

            AnalysisResult {
                race_id: race.race_id.clone(),
                checkmate_score: score,
                qualified: score >= settings.QUALIFICATION_SCORE,
                trifecta_factors: factors,
            }
        })
        .collect();

    RaceAnalysisResponse {
        results,
        processing_time_ms: start_time.elapsed().as_millis(),
    }
}

// --- FFI (Foreign Function Interface) for C# ---

/// # Safety
/// The caller must ensure that `input_json_ptr` is a valid, null-terminated
/// C string. The returned `*mut c_char` must be freed by the caller to avoid
/// memory leaks.
#[no_mangle]
pub extern "C" fn analyze_races_ffi(input_json_ptr: *const c_char) -> *mut c_char {
    if input_json_ptr.is_null() {
        return std::ptr::null_mut();
    }

    // 1. Safely convert C string to Rust string
    let input_cstr = unsafe { CStr::from_ptr(input_json_ptr) };
    let input_json = match input_cstr.to_str() {
        Ok(s) => s,
        Err(_) => return std::ptr::null_mut(), // Invalid UTF-8
    };

    // 2. Deserialize request
    let request: RaceAnalysisRequest = match serde_json::from_str(input_json) {
        Ok(req) => req,
        Err(_) => return std::ptr::null_mut(), // JSON parsing failed
    };

    // 3. Call the core logic
    let response = analyze_races_parallel(request);

    // 4. Serialize response
    let response_json = match serde_json::to_string(&response) {
        Ok(json) => json,
        Err(_) => return std::ptr::null_mut(), // JSON serialization failed
    };

    // 5. Convert Rust string to C string pointer
    match CString::new(response_json) {
        Ok(c_string) => c_string.into_raw(),
        Err(_) => std::ptr::null_mut(), // Should not happen if json is valid
    }
}

/// # Safety
/// This function must be called with a pointer that was previously obtained
/// from `analyze_races_ffi` to avoid memory corruption.
#[no_mangle]
pub extern "C" fn free_rust_string(s: *mut c_char) {
    if !s.is_null() {
        unsafe {
            let _ = CString::from_raw(s);
        }
    }
}