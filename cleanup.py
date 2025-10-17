import json
import os
import shutil
from pathlib import Path

def cleanup_project():
    """
    Removes files and directories that are not part of the official project
    structure defined in the FORTUNA JSON parts.
    """
    # --- Step 1: Define the "golden set" of expected files and directories ---
    golden_files = set()
    golden_dirs = set()

    json_parts = sorted([f for f in os.listdir('.') if f.startswith('FORTUNA_ALL_PART') and f.endswith('.JSON')])

    all_file_data = {}
    for part_file in json_parts:
        with open(part_file, 'r', encoding='utf-8') as f:
            all_file_data.update(json.load(f))

    for file_path_str in all_file_data.keys():
        p = Path(file_path_str)
        golden_files.add(p)
        # Add all parent directories to the set of golden directories
        for parent in p.parents:
            if parent != Path('.'): # Don't add the root directory itself
                golden_dirs.add(parent)

    # --- Step 2: Define files and directories to always ignore ---
    # This includes the script itself, the source JSONs, and core git/env files.
    ignore_list = {
        Path('.git'),
        Path('cleanup.py'),
        Path('reconstruct.py'),
        Path('.gitignore'),
        Path('.env'),
        Path('.key')
    }
    for part_file in json_parts:
        ignore_list.add(Path(part_file))

    # --- Step 3: Walk the repository and identify items to delete ---
    to_delete_files = []
    to_delete_dirs = []

    for root, dirs, files in os.walk('.', topdown=False): # topdown=False for post-order traversal
        root_path = Path(root)

        # Prune ignore list from directory traversal
        dirs[:] = [d for d in dirs if root_path / d not in ignore_list]

        # Check files for deletion
        for file_name in files:
            file_path = root_path / file_name
            if file_path not in golden_files and file_path not in ignore_list:
                to_delete_files.append(file_path)

        # Check directories for deletion (must be empty after files are removed)
        for dir_name in dirs:
            dir_path = root_path / dir_name
            if dir_path not in golden_dirs and dir_path not in ignore_list:
                # Check if directory will be empty after targeted file deletion
                contained_items = list((dir_path).glob('**/*'))
                contained_golden_files = any(f in golden_files for f in contained_items if f.is_file())
                if not contained_golden_files:
                     to_delete_dirs.append(dir_path)


    # --- Step 4: Perform the deletion ---
    print("--- Files to Delete ---")
    for f in to_delete_files:
        try:
            print(f"Deleting file: {f}")
            f.unlink()
        except OSError as e:
            print(f"Error deleting file {f}: {e}")

    print("\n--- Directories to Delete ---")
    for d in to_delete_dirs:
        try:
            # Check if directory is empty before deleting
            if not os.listdir(d):
                print(f"Deleting empty directory: {d}")
                d.rmdir()
            else:
                 # It might contain other directories that will be deleted, so use shutil.rmtree
                 print(f"Deleting directory and its contents: {d}")
                 shutil.rmtree(d)
        except OSError as e:
            print(f"Error deleting directory {d}: {e}")

    print("\nCleanup complete.")

if __name__ == "__main__":
    cleanup_project()