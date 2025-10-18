// rust_engine/tests/integration_tests.rs
// Establishes the foundational test suite for the Rust Analysis Core.

// This allows us to use the structs and functions from the main library
use checkmate_engine::*;

#[test]
fn test_perfect_race_is_qualified() {
    let settings = AnalysisSettings {
        qualification_score: 75.0,
        field_size_optimal_min: 4,
        field_size_optimal_max: 6,
        field_size_acceptable_min: 7,
        field_size_acceptable_max: 8,
        field_size_optimal_points: 30.0,
        field_size_acceptable_points: 10.0,
        field_size_penalty_points: -20.0,
        fav_odds_points: 30.0,
        max_fav_odds: 3.5,
        second_fav_odds_points: 40.0,
        min_2nd_fav_odds: 4.0,
    };

    let race = RaceData {
        race_id: "test_perfect_1".to_string(),
        runners: vec![
            Runner { name: "A".to_string(), odds: Some(2.5) },
            Runner { name: "B".to_string(), odds: Some(5.0) },
            Runner { name: "C".to_string(), odds: Some(10.0) },
            Runner { name: "D".to_string(), odds: Some(12.0) },
            Runner { name: "E".to_string(), odds: Some(15.0) },
        ],
    };

    let result = analyze_single_race(&race, &settings);

    assert!(result.qualified);
    assert_eq!(result.checkmate_score, 100.0);
}

#[test]
fn test_weak_favorite_is_not_qualified() {
    let settings = AnalysisSettings { // Using default settings for this test
        qualification_score: 75.0,
        field_size_optimal_min: 4,
        field_size_optimal_max: 6,
        field_size_acceptable_min: 7,
        field_size_acceptable_max: 8,
        field_size_optimal_points: 30.0,
        field_size_acceptable_points: 10.0,
        field_size_penalty_points: -20.0,
        fav_odds_points: 30.0,
        max_fav_odds: 3.5,
        second_fav_odds_points: 40.0,
        min_2nd_fav_odds: 4.0,
    };

    let race = RaceData {
        race_id: "test_weak_fav_1".to_string(),
        runners: vec![
            Runner { name: "WeakFav".to_string(), odds: Some(4.0) }, // Odds > max_fav_odds
            Runner { name: "B".to_string(), odds: Some(5.0) },
            Runner { name: "C".to_string(), odds: Some(6.0) },
            Runner { name: "D".to_string(), odds: Some(7.0) },
        ],
    };

    let result = analyze_single_race(&race, &settings);

    assert!(!result.qualified);
}