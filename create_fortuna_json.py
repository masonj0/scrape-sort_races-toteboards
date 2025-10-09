# create_fortuna_json.py
# This script now contains the full, enlightened logic to handle all manifest formats and path styles.

import json
import os
import re
import sys

# --- Configuration ---
MANIFEST_FILES = ['MANIFEST2.md', 'MANIFEST3.md']
OUTPUT_FILE_PART1 = 'FORTUNA_ALL_PART1.JSON' # Backend & Tests
OUTPUT_FILE_PART2 = 'FORTUNA_ALL_PART2.JSON' # Frontend, Docs, & Tooling

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

def main():
    print(f"\n{'='*60}\nStarting FORTUNA Dossier creation process... (Two Dossier Edition)\n{'='*60}")

    all_links = []
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

    part1_data = {} # Backend & Tests
    part2_data = {} # Frontend, Docs, & Tooling
    failed_count = 0
    unique_local_paths = sorted(list(set(all_local_paths)))

    print(f"\nFound a total of {len(unique_local_paths)} unique files to categorize and process.")

    for link in unique_links:
        try:
            # THIS LOGIC IS A VERBATIM COPY FROM convert_to_json.py
            local_path = '/'.join(link.split('/main/')[1:])
            print(f"--> Processing: {local_path}")

            if not os.path.exists(local_path):
                print(f"    [ERROR] File not found on disk: {local_path}")
                failed_count += 1
                continue

            with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # --- Categorization Logic ---
            if (local_path.startswith('python_service/') or local_path.startswith('tests/')):
                part1_data[local_path] = content
            else:
                part2_data[local_path] = content

        except Exception as e:
            print(f"    [ERROR] Failed to read {link}: {e}")
            failed_count += 1

    # --- Write Part 1 ---
    print(f"\nWriting {len(part1_data)} files to {OUTPUT_FILE_PART1}...")
    with open(OUTPUT_FILE_PART1, 'w', encoding='utf-8') as f:
        json.dump(part1_data, f, indent=4)
    print(f"    [SUCCESS] {OUTPUT_FILE_PART1} created.")

    # --- Write Part 2 ---
    print(f"Writing {len(part2_data)} files to {OUTPUT_FILE_PART2}...")
    with open(OUTPUT_FILE_PART2, 'w', encoding='utf-8') as f:
        json.dump(part2_data, f, indent=4)
    print(f"    [SUCCESS] {OUTPUT_FILE_PART2} created.")

    print(f"\n{'='*60}\nPackaging process complete.\nSuccessfully processed: {len(part1_data) + len(part2_data)}/{len(unique_local_paths)}\nFailed/Skipped: {failed_count}\n{'='*60}")

    if failed_count > 0:
        print("\n[WARNING] Some files failed to process. The output may be incomplete.")
        sys.exit(1)

if __name__ == "__main__":
    main()