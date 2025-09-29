use criterion::{criterion_group, criterion_main, Criterion};
use checkmate_engine::{RaceAnalysisRequest, analyze_single_race_advanced, generate_benchmark_races, create_default_settings}; // Assuming these exist in lib.rs
use rayon::prelude::*;

fn run_parallel_benchmark(c: &mut Criterion) {
    let test_races = generate_benchmark_races(1000);
    let settings = create_default_settings();
    let request = RaceAnalysisRequest { races: test_races, settings };

    c.bench_function("Parallel Analysis of 1000 Races", |b| {
        b.iter(|| {
            // The code to be benchmarked goes here
            let _results: Vec<_> = request.races
                .par_iter()
                .map(|race| analyze_single_race_advanced(race, &request.settings))
                .collect();
        })
    });
}

criterion_group!(benches, run_parallel_benchmark);
criterion_main!(benches);