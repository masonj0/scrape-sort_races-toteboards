# ARCHIVE_PROJECT.py - The True Scribe
# This script is the single source of truth for generating the FORTUNA_ALL JSON archives.

import os
import json
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent
OUTPUT_FILENAME_TEMPLATE = "FORTUNA_ALL_PART{}.JSON"
IGNORE_PATTERNS = {
    '.git', '.idea', '.vscode', '__pycache__', '.venv', 'node_modules',
    'build', 'dist', 'logs', '.DS_Store', '.pytest_cache', '.next',
    'pip_install.log', 'npm_install.log', 'electron_install.log', 'ReviewableJSON',
    '*.pyc', '*.egg-info', 'MANIFEST.md', 'MANIFEST2.md', 'MANIFEST3.md',
    'FORTUNA_ALL_PART*.JSON', 'PREV_*',
    # Exclude the deprecated and new archive scripts themselves
    'create_fortuna_json.py', 'MANAGE_MANIFESTS.py', 'ARCHIVE_PROJECT.py'
}

def categorize_file(relative_path: str) -> int:
    """Intelligently categorizes a file into its correct archive part."""
    path = Path(relative_path)
    if path.parts[0] == 'python_service' and path.parts[1] != 'adapters':
        return 1  # Part 1: Backend Core, Tests, Schemas
    if path.parts[0] == 'tests' or path.parts[0] == 'pg_schemas':
        return 1
    if path.parts[0] == 'python_service' and path.parts[1] == 'adapters':
        return 2  # Part 2: The Adapter Fleet
    if path.parts[0] in ['web_platform', 'electron']:
        return 3  # Part 3: The Frontend Pillar
    # Everything else goes to the operator's toolkit and documentation
    return 4  # Part 4: Windows Tooling, Root Scripts, Docs

def should_ignore(path: Path) -> bool:
    """Checks if a file or directory should be ignored."""
    return any(p in IGNORE_PATTERNS for p in path.parts) or \
           any(path.match(pattern) for pattern in IGNORE_PATTERNS)

def run_archiver():
    print("--- Fortuna Faucet True Scribe ---")
    print("Scanning project and generating complete archives...")

    archives = {1: {}, 2: {}, 3: {}, 4: {}}
    file_count = 0

    for root, dirs, files in os.walk(PROJECT_ROOT, topdown=True):
        # Prune ignored directories to prevent descending into them
        dirs[:] = [d for d in dirs if not should_ignore(Path(root) / d)]

        for file in files:
            file_path = Path(root) / file
            if should_ignore(file_path):
                continue

            relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()
            category = categorize_file(relative_path)

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                archives[category][relative_path] = content
                file_count += 1
            except Exception as e:
                print(f"[ERROR] Could not read file {relative_path}: {e}")

    print(f"\nScanned and categorized {file_count} project files.")

    # Write the four JSON archive files
    for part_num, content_dict in archives.items():
        output_path = PROJECT_ROOT / OUTPUT_FILENAME_TEMPLATE.format(part_num)
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(content_dict, f, indent=4)
            print(f"Successfully wrote {len(content_dict)} files to {output_path.name}")
        except Exception as e:
            print(f"[FATAL] Failed to write {output_path.name}: {e}")

    print("\n[SUCCESS] All archives are complete and correct!")

if __name__ == "__main__":
    run_archiver()