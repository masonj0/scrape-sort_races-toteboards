# convert_to_json.py

import json
import os
import re
import sys
from multiprocessing import Process, Queue

# --- Configuration ---
MANIFEST_FILES = ['MANIFEST2.md', 'MANIFEST3.md']
OUTPUT_DIR = 'ReviewableJSON'
FILE_PROCESSING_TIMEOUT = 10  # Seconds to wait before killing a hung file read

# --- Core Functions ---
def parse_manifest_for_links(manifest_path):
    """Parses a manifest file to extract raw GitHub file links."""
    if not os.path.exists(manifest_path):
        return []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return re.findall(r'(https://raw\.githubusercontent\.com/masonj0/scrape-sort_races-toteboards/refs/heads/main/[-/\w\.]+)', content)

def _sandboxed_file_read(file_path, q):
    """This function runs in a separate process to read a file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        q.put({"file_path": file_path, "content": content})
    except Exception as e:
        q.put({"error": str(e)})

def convert_file_to_json_sandboxed(file_path):
    """Reads a file in a sandboxed process with a timeout."""
    q = Queue()
    p = Process(target=_sandboxed_file_read, args=(file_path, q))
    p.start()
    p.join(timeout=FILE_PROCESSING_TIMEOUT)

    if p.is_alive():
        p.terminate()
        p.join() # Ensure termination is complete
        return {"error": f"Timeout: File processing took longer than {FILE_PROCESSING_TIMEOUT} seconds."}

    if not q.empty():
        return q.get()
    return {"error": "Unknown error in sandboxed read process."}

# --- Main Orchestrator ---
def main():
    print(f"\n{'='*60}\nStarting IRONCLAD JSON backup process...\n{'='*60}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_links = []
    for manifest in MANIFEST_FILES:
        print(f"--> Parsing manifest: {manifest}")
        links = parse_manifest_for_links(manifest)
        all_links.extend(links)
        print(f"    --> Found {len(links)} links.")

    if not all_links:
        print("\n[FATAL] No links found in any manifest. Aborting.")
        return

    print(f"\nFound a total of {len(all_links)} unique files to process.")
    processed_count, failed_count = 0, 0

    for link in set(all_links): # Use set to avoid processing duplicate links
        local_path = '/'.join(link.split('/main/')[1:])
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

    print(f"\n{'='*60}\nBackup process complete.\nSuccessfully processed: {processed_count}/{len(all_links)}\nFailed/Skipped: {failed_count}\n{'='*60}")

    if failed_count > 0:
        sys.exit(1) # Exit with an error code if any files failed

if __name__ == "__main__":
    main()