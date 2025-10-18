# convert_to_json.py
# This script now contains the full, enlightened logic to handle all manifest formats and path styles.

import json
import os
import re
import sys
from multiprocessing import Process, Queue

# --- Configuration ---
MANIFEST_FILES = ['MANIFEST2.md', 'MANIFEST3.md']
OUTPUT_DIR = 'ReviewableJSON'
FILE_PROCESSING_TIMEOUT = 10

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

# --- SANDBOXED FILE READ (Unchanged) ---
def _sandboxed_file_read(file_path, q):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        q.put({"file_path": file_path, "content": content})
    except Exception as e:
        q.put({"error": str(e)})

def convert_file_to_json_sandboxed(file_path):
    q = Queue()
    p = Process(target=_sandboxed_file_read, args=(file_path, q))
    p.start()
    p.join(timeout=FILE_PROCESSING_TIMEOUT)
    if p.is_alive():
        p.terminate()
        p.join()
        return {"error": f"Timeout: File processing took longer than {FILE_PROCESSING_TIMEOUT} seconds."}
    if not q.empty():
        return q.get()
    return {"error": "Unknown error in sandboxed read process."}

# --- Main Orchestrator ---
def main():
    print(f"\n{'='*60}\nStarting IRONCLAD JSON backup process... (Enlightened Scribe Edition)\n{'='*60}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

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

    unique_local_paths = sorted(list(set(all_local_paths)))
    print(f"\nFound a total of {len(unique_local_paths)} unique files to process.")
    processed_count, failed_count = 0, 0

    for local_path in unique_local_paths:
        print(f"\nProcessing: {local_path}")
        json_data = convert_file_to_json_sandboxed(local_path)
        if json_data and "error" not in json_data:
            output_path = os.path.join(OUTPUT_DIR, local_path + '.json')
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=4)
            print(f"    [SUCCESS] Saved backup to {output_path}")
            processed_count += 1
        else:
            error_msg = json_data.get("error", "Unknown error") if json_data else "File not found"
            print(f"    [ERROR] Failed to process {local_path}: {error_msg}")
            failed_count += 1

    print(f"\n{'='*60}\nBackup process complete.\nSuccessfully processed: {processed_count}/{len(unique_local_paths)}\nFailed/Skipped: {failed_count}\n{'='*60}")

    if failed_count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()