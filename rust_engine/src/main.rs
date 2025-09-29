// In rust_engine/src/main.rs
use std::env;
use std::io::{self, Read};
use checkmate_engine::{RaceAnalysisRequest, RaceAnalysisResponse, analyze_single_race_advanced}; // Assuming these are in lib.rs
use rayon::prelude::*;
use num_cpus;

fn main() {
    // --- DYNAMIC THREAD POOL CONFIGURATION ---
    // This should be done once at the very start of the program.
    rayon::ThreadPoolBuilder::new()
        .num_threads(num_cpus::get()) // Sets thread count to the number of logical CPUs
        .build_global()
        .unwrap(); // This unwrap is acceptable on startup; if it fails, the app can't run.

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
    if let Err(e) = io::stdin().read_to_string(&mut input) {
        eprintln!("[ERROR] Failed to read from stdin: {}", e);
        std::process::exit(1);
    }

    // Call the core logic and handle the Result
    match run_analysis_from_json(&input) {
        Ok(response) => {
            // Using unwrap here is acceptable for a CLI tool's final output.
            // A failure to serialize a valid response struct is a critical, unrecoverable bug.
            println!("{}", serde_json::to_string_pretty(&response).unwrap());
        }
        Err(e) => {
            eprintln!("[ERROR] Analysis failed: {}", e);
            std::process::exit(1);
        }
    }
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