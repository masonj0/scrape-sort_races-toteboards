import json
import os
import sys

def convert_file_to_json(filepath):
    """Reads a file and converts its content to a JSON structure."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        json_data = {
            "filepath": filepath,
            "content": content
        }

        # Create the output path in the ReviewableJSON directory
        output_filename = os.path.basename(filepath) + ".json"
        output_path = os.path.join("ReviewableJSON", output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)

        print(f"Successfully converted {filepath} to {output_path}")

    except Exception as e:
        print(f"Error converting {filepath}: {e}", file=sys.stderr)

if __name__ == "__main__":
    # The file paths will be passed as command-line arguments
    for filepath in sys.argv[1:]:
        convert_file_to_json(filepath)
