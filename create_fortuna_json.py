# create_fortuna_json.py
# This script now dynamically reads the manifests and creates four separate, categorized JSON packages.

import json
import os
import re
import sys

# --- Configuration ---
MANIFEST_FILES = ['MANIFEST.md', 'MANIFEST2.md', 'MANIFEST3.md']
OUTPUT_FILE_PART1 = 'FORTUNA_ALL_PART1.JSON' # Core Web Service
OUTPUT_FILE_PART2 = 'FORTUNA_ALL_PART2.JSON' # Adapter Fleet
OUTPUT_FILE_PART3 = 'FORTUNA_ALL_PART3.JSON' # Frontend Application
OUTPUT_FILE_PART4 = 'FORTUNA_ALL_PART4.JSON' # Windows Tooling & Project Governance

WINDOWS_TOOLING_FILES = [
    'windows_service.py',
    'fortuna_monitor.py',
    'setup_wizard.py',
    'launcher.py',
    'python_service/etl.py'
]

# --- Logic ---
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
    md_match = re.search(r'\(([^)]+)\)', line)
    if md_match:
        path = md_match.group(1)
    else:
        # 2. Check for paths in backticks
        bt_match = re.search(r'`([^`]+)`', line)
        if bt_match:
            path = bt_match.group(1)
        else:
            # 3. Assume plain path, stripping list markers and descriptions
            path = re.sub(r'^[*-]\s*', '', line).split(' ')[0]

    # --- Path Standardization ---
    if not path or not ('.' in path or '/' in path):
        return None  # Filter out non-path lines

    if path.startswith('https://raw.githubusercontent.com/'):
        path = '/'.join(path.split('/main/')[1:])

    return path.strip()

def main():
    print("Starting FORTUNA Quarto Dossier creation...")
    all_local_paths = []
    for manifest in MANIFEST_FILES:
        if not os.path.exists(manifest):
            print(f"[WARNING] Manifest not found: {manifest}")
            continue
        with open(manifest, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                path = extract_and_normalize_path(line)
                if path and os.path.exists(path):
                    all_local_paths.append(path)

    part1_data, part2_data, part3_data, part4_data = {}, {}, {}, {}
    unique_local_paths = sorted(list(set(all_local_paths)))

    for local_path in unique_local_paths:
        with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # --- Categorization Logic (Quarto) ---
        if local_path.startswith('python_service/adapters/'):
            part2_data[local_path] = content
        elif local_path.startswith('web_platform/') or local_path.startswith('electron/'):
            part3_data[local_path] = content
        elif local_path in WINDOWS_TOOLING_FILES or local_path.endswith(('.bat', '.ps1', '.md')) or local_path.startswith('attic/'):
            part4_data[local_path] = content
        elif local_path.startswith('python_service/'):
            part1_data[local_path] = content
        else:
            # Default catch-all for any other root files
            part4_data[local_path] = content

    # --- Write Files ---
    for i, (data, path) in enumerate([
        (part1_data, OUTPUT_FILE_PART1),
        (part2_data, OUTPUT_FILE_PART2),
        (part3_data, OUTPUT_FILE_PART3),
        (part4_data, OUTPUT_FILE_PART4)
    ]):
        print(f"Writing {len(data)} files to {path}...")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"    [SUCCESS] Part {i+1} created.")

    print("\nPackaging process complete.")

if __name__ == "__main__":
    main()
