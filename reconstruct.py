import json
import os
from pathlib import Path

def reconstruct_project():
    """
    Reconstructs the project file structure from multiple JSON parts.
    """
    all_files = {}
    json_parts = [f for f in os.listdir('.') if f.startswith('FORTUNA_ALL_PART') and f.endswith('.JSON')]
    json_parts.sort() # Ensure they are loaded in order

    print(f"Found JSON parts: {json_parts}")

    for part_file in json_parts:
        try:
            with open(part_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_files.update(data)
            print(f"Successfully loaded and merged {part_file}")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {part_file}: {e}")
        except Exception as e:
            print(f"An error occurred while reading {part_file}: {e}")

    print(f"Total files to reconstruct: {len(all_files)}")

    for file_path, content in all_files.items():
        try:
            # Normalize path separators for the current OS
            normalized_path = Path(file_path)

            # Create parent directories if they don't exist
            normalized_path.parent.mkdir(parents=True, exist_ok=True)

            # Write the file content
            # Ensure content is a string, handle None or other types gracefully
            file_content = content if isinstance(content, str) else ''
            with open(normalized_path, 'w', encoding='utf-8') as f:
                f.write(file_content)

            # print(f"Created/overwrote file: {file_path}")

        except Exception as e:
            print(f"Failed to create file {file_path}: {e}")

    print("Reconstruction complete.")

if __name__ == "__main__":
    reconstruct_project()