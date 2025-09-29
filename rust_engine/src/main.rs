// In rust_engine/src/main.rs
use std::env;
use std::io::{self, Read};
use checkmate_engine::{RaceAnalysisRequest, RaceAnalysisResponse, analyze_single_race_advanced}; // Assuming these are in lib.rs
use rayon::prelude::*;

fn main() {
    let args: Vec<String> = env::args().collect();
    let command = args.get(1).map(|s| s.as_str());

    match command {
        Some("--analyze") => cli_analysis_mode(),
        Some("--benchmark") => benchmark_mode(),
        // Some("--server") => server_mode(), // Future placeholder
        Some("--help") | _ => print_help(),
    }
}

fn cli_analysis_mode() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).expect("Failed to read from stdin");

    let request: RaceAnalysisRequest = serde_json::from_str(&input)
        .expect("Failed to parse JSON input");

    let results: Vec<_> = request.races.par_iter()
        .map(|race| analyze_single_race_advanced(race, &request.settings))
        .collect();

    let response = RaceAnalysisResponse {
        results,
        // ... other metadata from V8 spec
    };

    println!("{}", serde_json::to_string_pretty(&response).unwrap());
}

fn benchmark_mode() {
    println!("🚀 Checkmate Rust Engine Benchmark Mode");
    // Implementation as per the V8 spec:
    // 1. Generate 1000 test races.
    // 2. Run analysis serially and time it.
    // 3. Run analysis in parallel and time it.
    // 4. Print speedup factor and other metrics.
    println!("Benchmark feature not yet fully implemented.");
}

fn print_help() {
    println!("Checkmate Rust Analysis Engine");
    println!("Usage: checkmate_engine [COMMAND]");
    println!("\nCommands:");
    println!("  --analyze      Accepts JSON from stdin for analysis.");
    println!("  --benchmark    Runs a performance benchmark.");
    println!("  --help         Displays this help message.");
}