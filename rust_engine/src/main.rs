// src/main.rs - The CLI entry point for the Rust engine.

// This allows the binary to use the library's code.
use checkmate_engine_lib::*;
use std::io::{self, Read};

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() > 1 && args[1] == "--analyze" {
        let mut input = String::new();
        io::stdin().read_to_string(&mut input).expect("Failed to read from stdin");

        match serde_json::from_str::<RaceAnalysisRequest>(&input) {
            Ok(request) => {
                let response = analyze_races_parallel(request);
                println!("{}", serde_json::to_string(&response).unwrap());
            }
            Err(e) => {
                eprintln!("JSON parsing error in Rust engine: {}", e);
                std::process::exit(1);
            }
        }
    } else {
        eprintln!("Usage: {} --analyze", args[0]);
        std::process::exit(1);
    }
}