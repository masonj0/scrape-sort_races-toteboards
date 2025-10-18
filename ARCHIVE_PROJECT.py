# ARCHIVE_PROJECT.py - The Manifest-Driven Scribe
# This script generates the FORTUNA_ALL JSON archives based on the new JSON manifests.

import os
import json
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent
OUTPUT_FILENAME_TEMPLATE = "FORTUNA_ALL_PART{}.JSON"

# Map manifest files to their corresponding archive part number
MANIFEST_MAP = {
    "MANIFEST_BACKEND.json": 1,
    "MANIFEST_SCRIPTS.json": 2,
    "MANIFEST_FRONTEND.json": 3,
    "MANIFEST_ROOT.json": 4
}

def run_archiver():
    print("--- Fortuna Faucet Manifest-Driven Scribe ---")
    print("Generating archives from JSON manifests...")

    archives = {1: {}, 2: {}, 3: {}, 4: {}}
    total_files_archived = 0

    for manifest_file, part_num in MANIFEST_MAP.items():
        manifest_path = PROJECT_ROOT / manifest_file

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                file_list = json.load(f)
        except FileNotFoundError:
            print(f"[ERROR] Manifest file not found: {manifest_file}. Skipping.")
            continue
        except json.JSONDecodeError:
            print(f"[ERROR] Could not decode JSON from {manifest_file}. Skipping.")
            continue

        print(f"Processing {manifest_file} for PART {part_num}...")
        for relative_path in file_list:
            file_path = PROJECT_ROOT / relative_path
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                archives[part_num][relative_path] = content
                total_files_archived += 1
            except FileNotFoundError:
                print(f"[WARNING] File listed in manifest not found: {relative_path}")
            except Exception as e:
                print(f"[ERROR] Could not read file {relative_path}: {e}")

    print(f"\nProcessed {total_files_archived} files across {len(MANIFEST_MAP)} manifests.")

    # Write the four JSON archive files
    for part_num, content_dict in archives.items():
        if not content_dict:
            print(f"Skipping empty PART {part_num}.")
            continue

        output_path = PROJECT_ROOT / OUTPUT_FILENAME_TEMPLATE.format(part_num)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content_dict, f, indent=4)
            print(f"✅ Successfully wrote {len(content_dict)} files to {output_path.name}")
        except Exception as e:
            print(f"[FATAL] Failed to write {output_path.name}: {e}")

    print("\n[SUCCESS] All manifest-driven archives are complete!")

if __name__ == "__main__":
    run_archiver()
