// src/main.rs - The CLI entry point for the Python service.

// This allows our binary to use the functions from our library.
use checkmate_engine_lib::*;
use std::io::{self, Read};

fn main() {
    let args: Vec<String> = std::env::args().collect();

    if args.len() > 1 && args[1] == "--analyze" {
        let mut input = String::new();
        io::stdin().read_to_string(&mut input).expect("Failed to read from stdin");

        // The FFI function handles all logic and prints the result to stdout.
        // We just need to call it and handle the pointer.
        let input_cstr = std::ffi::CString::new(input).unwrap();
        let result_ptr = analyze_races_ffi(input_cstr.as_ptr());

        if !result_ptr.is_null() {
            let result_str = unsafe { std::ffi::CStr::from_ptr(result_ptr).to_str().unwrap() };
            println!("{}", result_str);
            // IMPORTANT: Deallocate the memory that Rust allocated for the string.
            deallocate_rust_string(result_ptr);
        }
    } else {
        eprintln!("Usage: {} --analyze", args[0]);
        std::process::exit(1);
    }
}