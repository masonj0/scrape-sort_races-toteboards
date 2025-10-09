# create_fortuna_json.py
# This script now contains the full, enlightened logic to handle all manifest formats and path styles.

import json
import os
import re
import sys

# --- Configuration ---
MANIFEST_FILES = ['MANIFEST2.md', 'MANIFEST3.md']
OUTPUT_FILE = 'FORTUNA_ALL.JSON'

# --- ENLIGHTENED PARSING LOGIC (V2) ---
def extract_and_normalize_path(line: str) -> str | None:
    """
    Extracts a file path from a line, handling multiple formats, and normalizes it.
    Handles:
    - Markdown links: `* [display](path)`
    - Plain paths in backticks: ``- `path.py` - description``
    - Plain paths with list markers: `- path/to/file.py`
    """
    line = line.strip()
    if not line or line.startswith('#'):
        return None

    # 1. Check for Markdown link format
    md_match = re.search(r'\[.*\]\((https?://[^\)]+)\)', line)
    if md_match:
        path = md_match.group(1)
    else:
        # 2. Check for paths in backticks
        bt_match = re.search(r'`([^`]+)`', line)
        if bt_match:
            path = bt_match.group(1)
        else:
            # 3. Assume plain path, stripping list markers
            path = re.sub(r'^[*-]\s*', '', line).split(' ')[0]

    # --- Path Standardization ---
    if not path or not ('.' in path or '/' in path):
        return None # Not a valid path

    # If it's a full raw GitHub URL, extract the local path
    if path.startswith('https://raw.githubusercontent.com/'):
        path = '/'.join(path.split('/main/')[1:])

    # Final check for valid file extensions or structure
    if not re.search(r'(\.[a-zA-Z0-9]+$)|(^[\w/]+$)', path):
        return None

    return path.strip()

# --- Main Orchestrator ---
def main():
    print(f"\n{'='*60}\nStarting FORTUNA_ALL.JSON creation process... (Enlightened Scribe Edition)\n{'='*60}")

    all_local_paths = []
    for manifest in MANIFEST_FILES:
        print(f"--> Parsing manifest: {manifest}")
        if not os.path.exists(manifest):
            print(f"    [WARNING] Manifest not found: {manifest}")
            continue

        with open(manifest, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        paths_found = 0
        for line in lines:
            path = extract_and_normalize_path(line)
            if path:
                all_local_paths.append(path)
                paths_found += 1
        print(f"    --> Found {paths_found} valid file paths.")

    if not all_local_paths:
        print("\n[FATAL] No valid file paths found in any manifest. Aborting.")
        sys.exit(1)

    fortuna_data = {}
    processed_count = 0
    failed_count = 0
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