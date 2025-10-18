import os
import json

# --- CONFIGURATION ---
ROOT_DIR = '.'
OUTPUT_DIR = '.'

EXCLUDE_DIRS = {
    '.git',
    '.idea',
    '.vscode',
    'node_modules',
    '.venv',
    'dist',
    'build',
    '__pycache__',
    'attic',
    'installer',
    'ReviewableJSON',
    'PREV_src',
    '.pytest_cache'
}

EXCLUDE_FILES = {
    'MANIFEST_ROOT.json',
    'MANIFEST_BACKEND.json',
    'MANIFEST_FRONTEND.json',
    'MANIFEST_SCRIPTS.json',
    'FORTUNA_ALL_PART1.JSON',
    'FORTUNA_ALL_PART2.JSON',
    'FORTUNA_ALL_PART3.JSON',
    'FORTUNA_ALL_PART4.JSON',
    'FORTUNA_ALL_PART5.JSON',
    'generate_manifests.py',
    '.env',
    '.env.example',
    '.env.local.example',
    'env'
}

# Define the structure of our manifests
MANIFESTS = {
    'MANIFEST_ROOT.json': {'dirs': [], 'files': []},
    'MANIFEST_BACKEND.json': {'dirs': ['python_service', 'pg_schemas', 'tests'], 'files': []},
    'MANIFEST_FRONTEND.json': {'dirs': ['web_platform', 'electron'], 'files': []},
    'MANIFEST_SCRIPTS.json': {'dirs': ['scripts'], 'files': []}
}

def is_excluded(path, entry_name):
    """Check if a file or directory should be excluded."""
    # Exclude files starting with PREV_
    if entry_name.startswith('PREV_'):
        return True
    # Exclude specific directories
    if entry_name in EXCLUDE_DIRS:
        return True
    # Exclude specific files
    if entry_name in EXCLUDE_FILES:
        return True
    return False

def main():
    """Walk the directory and generate categorized manifest files."""
    all_files = []
    for root, dirs, files in os.walk(ROOT_DIR, topdown=True):
        # Modify dirs in-place to prevent walking into excluded directories
        dirs[:] = [d for d in dirs if not is_excluded(os.path.join(root, d), d)]

        for name in files:
            if not is_excluded(os.path.join(root, name), name):
                filepath = os.path.join(root, name).replace('\\\\', '/')
                # Skip the root './'
                if filepath.startswith('./'):
                    filepath = filepath[2:]
                all_files.append(filepath)

    # Categorize files into the manifests
    categorized_files = set()
    for manifest_name, criteria in MANIFESTS.items():
        manifest_files = []
        for f in all_files:
            if any(f.startswith(d) for d in criteria['dirs']):
                manifest_files.append(f)
                categorized_files.add(f)
        MANIFESTS[manifest_name]['files'] = sorted(manifest_files)

    # Handle root files (those not caught by other manifests)
    root_files = sorted(list(set(all_files) - categorized_files))
    MANIFESTS['MANIFEST_ROOT.json']['files'] = root_files

    # Write the manifest files
    for manifest_name, data in MANIFESTS.items():
        output_path = os.path.join(OUTPUT_DIR, manifest_name)
        with open(output_path, 'w') as f:
            json.dump(data['files'], f, indent=4)
        print(f"✅ Generated {output_path} with {len(data['files'])} entries.")

if __name__ == '__main__':
    main()
