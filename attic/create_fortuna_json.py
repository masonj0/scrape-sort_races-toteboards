import json
import os
from pathlib import Path

def create_fortuna_json(root_dir=".", output_file="fortuna.json"):
    """
    Scans a directory, reads all files, and compiles their content into a single JSON object.

    Args:
        root_dir (str): The root directory to start scanning from.
        output_file (str): The name of the output JSON file.
    """
    fortuna_data = {}
    root_path = Path(root_dir)

    # List of directories and files to ignore
    ignore_list = {
        ".git",
        ".idea",
        "__pycache__",
        "node_modules",
        ".DS_Store",
        "dist",
        "build",
        "*.pyc",
        "*.log",
        "*.json",
        ".gitignore"
        "attic",
        "ARCHIVE_PROJECT.py",
        "create_fortuna_json.py"
    }

    for path in root_path.rglob("*"):
        if any(part in ignore_list for part in path.parts):
            continue

        if path.is_file():
            try:
                relative_path = path.relative_to(root_path)
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                # Create nested dictionary structure based on file path
                parts = list(relative_path.parts)
                current_level = fortuna_data
                for part in parts[:-1]:
                    current_level = current_level.setdefault(part, {})

                current_level[parts[-1]] = content

            except Exception as e:
                print(f"Error reading file {path}: {e}")

    # Write the collected data to the output JSON file
    try:
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(fortuna_data, f, indent=4)
        print(f"Successfully created {output_file}")
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    # By default, this script will scan its own directory.
    # To scan a different directory, provide the path as a command-line argument.
    # For example: python create_fortuna_json.py /path/to/your/project
    import sys

    # Check if a directory path is provided as a command-line argument
    if len(sys.argv) > 1:
        start_dir = sys.argv[1]
        if not os.path.isdir(start_dir):
            print(f"Error: The provided path '{start_dir}' is not a valid directory.")
            sys.exit(1)
    else:
        # If no argument is provided, use the directory where the script is located
        start_dir = os.path.dirname(os.path.abspath(__file__))

    # Define the output file name
    json_output_file = "fortuna_gold.json"

    print(f"Scanning directory: {start_dir}")
    print(f"Output will be saved to: {json_output_file}")

    create_fortuna_json(root_dir=start_dir, output_file=json_output_file)