#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: Rebranding Audit Script
# ==============================================================================
# This script performs a comprehensive, read-only audit of the project to
# identify all files containing legacy branding terms.
# ==============================================================================

import os

# --- CONFIGURATION ---
TARGET_TERMS = ['checkmate', 'solo']
EXCLUDED_DIRS = ['.git', '.venv', 'node_modules', 'build', 'dist', '__pycache__', 'ReviewableJSON']
EXCLUDED_FILES = ['audit_rebranding.py', 'REBRANDING_AUDIT.md']
OUTPUT_FILE = 'REBRANDING_AUDIT.md'
# -------------------

def search_file_for_terms(file_path, terms):
    """Searches a single file for a list of terms, case-insensitively."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read().lower()
            for term in terms:
                if term in content:
                    return True
    except Exception as e:
        print(f"[WARNING] Could not read file {file_path}: {e}")
    return False

def main():
    """Main orchestrator for the audit."""
    print("--- Starting Rebranding Audit ---")
    affected_files = []
    for root, dirs, files in os.walk('.', topdown=True):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

        for filename in files:
            if filename in EXCLUDED_FILES:
                continue

            file_path = os.path.join(root, filename)

            # Check filename itself
            if any(term in filename.lower() for term in TARGET_TERMS):
                affected_files.append(file_path)
                print(f"[FOUND] Legacy term in filename: {file_path}")
                continue # No need to search content if filename matches

            # Check file content
            if search_file_for_terms(file_path, TARGET_TERMS):
                affected_files.append(file_path)
                print(f"[FOUND] Legacy term in content: {file_path}")

    print(f"\n--- Audit Complete. Found {len(affected_files)} affected files. ---")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('# Fortuna Faucet: Rebranding Audit Report\n\n')
        f.write('This report lists all files containing legacy branding terms (`checkmate`, `solo`).\n\n---\n\n')
        if affected_files:
            for file_path in sorted(affected_files):
                f.write(f"- `{file_path.replace(os.sep, '/')}`\n")
        else:
            f.write('No files with legacy branding were found.\n')

    print(f"[SUCCESS] Report written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()