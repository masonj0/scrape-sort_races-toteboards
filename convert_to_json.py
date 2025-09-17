import json
import os
import sys

def convert_file_to_json(filepath):
    """Reads a file and converts its content to a JSON structure, preserving directory structure."""
    try:
        # Normalize path to use forward slashes for consistency
        normalized_filepath = filepath.replace("\\", "/")

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        json_data = {
            "filepath": normalized_filepath,
            "content": content
        }

        # Create the output path in the ReviewableJSON directory, preserving the original path
        # Remove './' prefix if it exists
        if normalized_filepath.startswith('./'):
            normalized_filepath = normalized_filepath[2:]

        output_dir = os.path.join("ReviewableJSON", os.path.dirname(normalized_filepath))
        if output_dir: # Only create directory if it's not the root
            os.makedirs(output_dir, exist_ok=True)

        output_filename = os.path.basename(normalized_filepath) + ".json"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)

        print(f"Successfully converted {filepath} to {output_path}")

    except Exception as e:
        print(f"Error converting {filepath}: {e}", file=sys.stderr)

if __name__ == "__main__":
    # Walk through the directory tree and convert all .py files
    for root, dirs, files in os.walk("."):
        # Exclude specified directories from the walk
        dirs[:] = [d for d in dirs if d not in ['venv', '.venv', 'ReviewableJSON', '.git', '__pycache__']]

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                convert_file_to_json(filepath)
