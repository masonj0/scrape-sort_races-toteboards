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
def parse_manifest_for_links(manifest_path):
    """Parses a manifest file to extract raw GitHub file links."""
    if not os.path.exists(manifest_path):
        print(f"    [WARNING] Manifest not found: {manifest_path}")
        return []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # This regex now finds both markdown links and plain text paths
    plain_paths = re.findall(r'^- `(.+?)`', content, re.MULTILINE)
    markdown_links = re.findall(r'\[(.+?)\]\((https://raw\.githubusercontent\.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/[-/\w\.]+)\)', content)

    # Extract path from the link tuple
    linked_paths = [link.split('/main/')[1] for _, link in markdown_links]

    return plain_paths + linked_paths

# --- Main Orchestrator ---
def main():
    print(f"\n{'='*60}\nStarting FORTUNA_ALL.JSON creation process...\n{'='*60}")

    all_paths = []
    for manifest in MANIFEST_FILES:
        print(f"--> Parsing manifest: {manifest}")
        paths = parse_manifest_for_links(manifest)
        all_paths.extend(paths)
        print(f"    --> Found {len(paths)} paths.")

    if not all_paths:
        print("\n[FATAL] No paths found in any manifest. Aborting.")
        sys.exit(1)

    fortuna_data = {}
    processed_count = 0
    failed_count = 0
    unique_paths = sorted(list(set(all_paths))) # Use a sorted list for consistent order

    print(f"\nFound a total of {len(unique_paths)} unique files to process.")

    for local_path in unique_paths:
        try:
            print(f"--> Processing: {local_path}")

            if not os.path.exists(local_path):
                print(f"    [ERROR] File not found locally: {local_path}")
                failed_count += 1
                continue

            with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            fortuna_data[local_path] = content
            processed_count += 1
        except Exception as e:
            print(f"    [ERROR] Failed to process {local_path}: {e}")
            failed_count += 1

    print(f"\nWriting {len(fortuna_data)} files to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(fortuna_data, f, indent=4)

    print(f"\n{'='*60}\nPackaging process complete.\nSuccessfully processed: {processed_count}/{len(unique_paths)}\nFailed/Skipped: {failed_count}\n{'='*60}")

    if failed_count > 0:
        print("\n[WARNING] Some files failed to process. The output may be incomplete.")
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] {OUTPUT_FILE} created successfully.")

if __name__ == "__main__":
    main()