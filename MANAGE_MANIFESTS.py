# MANAGE_MANIFESTS.py
# An intelligent utility to audit and manage the project's manifest files.

import os
from pathlib import Path

# --- Configuration ---
PROJECT_ROOT = Path(__file__).parent
MANIFEST_FILES = [
    PROJECT_ROOT / 'MANIFEST.md',
    PROJECT_ROOT / 'MANIFEST2.md',
    PROJECT_ROOT / 'MANIFEST3.md'
]
# Directories and files to explicitly ignore during the scan
IGNORE_PATTERNS = [
    '.git',
    '.idea',
    '.vscode',
    '__pycache__',
    '.venv',
    'node_modules',
    'build',
    'dist',
    'logs',
    '.DS_Store',
    '*.pyc',
    '*.log',
    '*.egg-info'
]

def get_all_project_files():
    """Scans the project directory and returns a set of all file paths."""
    project_files = set()
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_PATTERNS]

        for file in files:
            file_path = Path(root) / file
            # Check if the file or its parts match any ignore patterns
            if not any(part in IGNORE_PATTERNS for part in file_path.parts) and \
               not any(file_path.match(p) for p in IGNORE_PATTERNS):
                relative_path = file_path.relative_to(PROJECT_ROOT).as_posix()
                project_files.add(relative_path)

    return project_files

def get_all_manifested_files():
    """Reads all manifest files and returns a set of listed file paths."""
    manifested_files = set()
    for manifest_path in MANIFEST_FILES:
        if not manifest_path.exists():
            continue
        with open(manifest_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    manifested_files.add(line)
    return manifested_files

def categorize_file(file_path: str) -> int:
    """Categorizes a file into a manifest (1, 2, or 3) based on its path."""
    if 'python_service' in file_path or 'tests' in file_path or 'pg_schemas' in file_path:
        return 2 # Backend
    if 'web_platform' in file_path or 'electron' in file_path:
        return 3 # Frontend
    return 1 # Root / General

def run_manifest_manager():
    print("--- Fortuna Faucet Manifest Scribe ---")
    print("Auditing all project files against the manifests...")

    project_files = get_all_project_files()
    manifested_files = get_all_manifested_files()

    # Exclude the manifests themselves and this script from the check
    this_script_name = Path(__file__).name
    project_files.discard(this_script_name)
    for m in MANIFEST_FILES:
        project_files.discard(m.name)

    new_files = sorted(list(project_files - manifested_files))
    stale_files = sorted(list(manifested_files - project_files))

    if not new_files and not stale_files:
        print("\n[SUCCESS] All manifests are up to date! No action needed.")
        return

    # --- Report Discrepancies ---
    if new_files:
        print(f"\n[!] Found {len(new_files)} new, un-manifested files:")
        for file in new_files:
            print(f"  + {file}")

    if stale_files:
        print(f"\n[!] Found {len(stale_files)} stale file entries (file no longer exists):")
        for file in stale_files:
            print(f"  - {file}")

    # --- Interactive Fixing ---
    print("-" * 40)
    choice = input("Would you like to automatically fix these issues? (y/n): ").lower()
    if choice != 'y':
        print("Aborted. No changes were made.")
        return

    # Fix Stale Files
    if stale_files:
        print("\n[*] Removing stale file entries...")
        for manifest_path in MANIFEST_FILES:
            if not manifest_path.exists(): continue
            with open(manifest_path, 'r') as f:
                lines = f.readlines()
            with open(manifest_path, 'w') as f:
                for line in lines:
                    if line.strip() not in stale_files:
                        f.write(line)
        print(f"Removed {len(stale_files)} stale entries.")

    # Fix New Files
    if new_files:
        print("\n[*] Adding new files to the correct manifests...")
        additions = {1: [], 2: [], 3: []}
        for file in new_files:
            category = categorize_file(file)
            additions[category].append(file)

        for i in range(1, 4):
            if additions[i]:
                manifest_path = PROJECT_ROOT / f'MANIFEST{i if i > 1 else ""}.md'
                with open(manifest_path, 'a') as f:
                    f.write('\n# Added by Manifest Scribe\n')
                    for file in sorted(additions[i]):
                        f.write(f"{file}\n")
                print(f"Added {len(additions[i])} files to {manifest_path.name}")

    print("\n[SUCCESS] All manifests have been updated!")

if __name__ == "__main__":
    run_manifest_manager()