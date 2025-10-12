# create_fortuna_json.py
# This script now dynamically reads the manifests and creates five separate, categorized JSON packages.

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
OUTPUT_FILE_PART5 = 'FORTUNA_ALL_PART5.JSON' # Historical Archives (Attic)

WINDOWS_TOOLING_FILES = [
    'windows_service.py',
    'fortuna_monitor.py',
    'setup_wizard.py',
    'launcher.py',
    'python_service/etl.py'
]

# --- Logic ---
def extract_and_normalize_path(line: str) -> str | None:
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    md_match = re.search(r'\((.*?)\)', line)
    if md_match:
        path = md_match.group(1)
    else:
        path = line.strip('*').strip('-').strip().split('(')[0].strip()

    if path.startswith('https://raw.githubusercontent.com/'):
        path = '/'.join(path.split('/main/')[1:])
    return path

def main():
    print("Starting FORTUNA Pentad Dossier creation...")
    all_local_paths = []
    for manifest in MANIFEST_FILES:
        if not os.path.exists(manifest):
            print(f"[WARNING] Manifest not found: {manifest}")
            continue
        with open(manifest, 'r', encoding='utf-8') as f:
            for line in f.readlines():
                path = extract_and_normalize_path(line)
                if path and os.path.exists(path) and not os.path.isdir(path):
                    all_local_paths.append(path)

    # Manually scan the attic directory
    attic_paths = []
    if os.path.isdir('attic'):
        for root, _, files in os.walk('attic'):
            for file in files:
                attic_paths.append(os.path.join(root, file))

    all_local_paths.extend(attic_paths)

    part1, part2, part3, part4, part5 = {}, {}, {}, {}, {}
    unique_local_paths = sorted(list(set(all_local_paths)))

    for local_path in unique_local_paths:
        with open(local_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # --- Categorization Logic (Pentad) ---
        if local_path.startswith('attic/'):
            part5[local_path] = content
        elif local_path.startswith('python_service/adapters/'):
            part2[local_path] = content
        elif local_path.startswith('web_platform/') or local_path.startswith('electron/'):
            part3[local_path] = content
        elif local_path in WINDOWS_TOOLING_FILES or local_path.endswith(('.bat', '.ps1', '.md')):
            part4[local_path] = content
        elif local_path.startswith('python_service/'):
            part1[local_path] = content
        else:
            part4[local_path] = content # Catch-all for other root files

    # --- Write Files ---
    dossiers = [
        (part1, OUTPUT_FILE_PART1),
        (part2, OUTPUT_FILE_PART2),
        (part3, OUTPUT_FILE_PART3),
        (part4, OUTPUT_FILE_PART4),
        (part5, OUTPUT_FILE_PART5)
    ]
    for i, (data, path) in enumerate(dossiers):
        print(f"Writing {len(data)} files to {path}...")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"    [SUCCESS] Part {i+1} created.")

    print("\nPackaging process complete.")

if __name__ == "__main__":
    main()
