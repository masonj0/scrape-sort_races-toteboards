# create_fortuna_json.py
# This script now dynamically reads the manifests to create the FORTUNA_ALL.JSON package.

import json
import os
import re
import sys

# --- Configuration ---
MANIFEST_FILES = ['MANIFEST2.md', 'MANIFEST3.md']
OUTPUT_FILE = 'FORTUNA_ALL.JSON'

# --- Core Functions ---
def parse_manifest_for_paths(manifest_path):
    """Parses a manifest file to extract local file paths."""
    if not os.path.exists(manifest_path):
        print(f"    [WARNING] Manifest not found: {manifest_path}")
        return []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # This regex is the 'wisdom'. It finds the markdown links and extracts the local path part.
    links = re.findall(r'https://raw\.githubusercontent\.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/([-a-zA-Z0-9_/\\.]+)', content)
    return links

# --- Main Orchestrator ---
def main():
    print(f"\n{'='*60}\nStarting FORTUNA_ALL.JSON creation process... (Wise Scribe Edition)\n{'='*60}")

    all_local_paths = []
    for manifest in MANIFEST_FILES:
        print(f"--> Parsing manifest: {manifest}")
        local_paths = parse_manifest_for_paths(manifest)
        all_local_paths.extend(local_paths)
        print(f"    --> Found {len(local_paths)} file paths.")

    if not all_local_paths:
        print("\n[FATAL] No file paths found in any manifest. Aborting.")
        sys.exit(1)

    fortuna_data = {}
    processed_count = 0
    failed_count = 0
    # Use a sorted list of unique paths for consistent order and no duplicates
    unique_local_paths = sorted(list(set(all_local_paths)))

    print(f"\nFound a total of {len(unique_local_paths)} unique files to process.")

    for local_path in unique_local_paths:
        try:
            print(f"--> Processing: {local_path}")

            if not os.path.exists(local_path):
                print(f"    [ERROR] File not found on disk: {local_path}")
                failed_count += 1
                continue

            with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            fortuna_data[local_path] = content
            processed_count += 1
        except Exception as e:
            print(f"    [ERROR] Failed to read {local_path}: {e}")
            failed_count += 1

    print(f"\nWriting {len(fortuna_data)} files to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fortuna_data, f, indent=4)

    print(f"\n{'='*60}\nPackaging process complete.\nSuccessfully processed: {processed_count}/{len(unique_local_paths)}\nFailed/Skipped: {failed_count}\n{'='*60}")

    if failed_count > 0:
        print("\n[WARNING] Some files failed to process. The output may be incomplete.")
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] {OUTPUT_FILE} created successfully.")

if __name__ == "__main__":
    main()