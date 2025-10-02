import json
import os
import sys

def convert_file_to_json(filepath):
    """Reads a file and converts its content to a JSON structure, preserving directory structure."""
    try:
        if not os.path.exists(filepath):
            print(f"Warning: File not found, skipping: {filepath}", file=sys.stderr)
            return

        # Normalize path to use forward slashes for consistency
        normalized_filepath = filepath.replace("\\", "/")

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        json_data = {
            "filepath": normalized_filepath,
            "content": content
        }

        # Create the output path in the ReviewableJSON directory, preserving the original path
        if normalized_filepath.startswith('./'):
            normalized_filepath = normalized_filepath[2:]

        output_dir = os.path.join("ReviewableJSON", os.path.dirname(normalized_filepath))
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        output_filename = os.path.basename(normalized_filepath) + ".json"
        output_path = os.path.join(output_dir, output_filename)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=4)

        print(f"Successfully converted {filepath} to {output_path}")

    except Exception as e:
        print(f"Error converting {filepath}: {e}", file=sys.stderr)

if __name__ == "__main__":
    # This list is generated from MANIFEST2.md and MANIFEST3.md to ensure a complete backup.
    files_to_convert = [
        # From MANIFEST2.md (CORE Architecture)
        ".env",
        "ARCHITECTURAL_MANDATE.md",
        "README.md",
        "STATUS.md",
        "setup_windows.bat",
        "python_service/api.py",
        "python_service/engine.py",
        "python_service/models.py",
        "python_service/requirements.txt",
        "python_service/adapters/__init__.py",
        "python_service/adapters/base.py",
        "python_service/adapters/betfair_adapter.py",
        "python_service/adapters/pointsbet_adapter.py",
        "python_service/adapters/racing_and_sports_adapter.py",
        "python_service/adapters/tvg_adapter.py",
        "python_service/adapters/utils.py",
        "web_platform/frontend/src/app/page.tsx",

        # From MANIFEST3.md (Operational & Tooling)
        # Strategic Blueprints & Sacred Texts
        "HISTORY.md",
        "WISDOM.md",
        "PROJECT_MANIFEST.md",
    ]

    print("Starting conversion based on the final manifest...")
    for filepath in files_to_convert:
        convert_file_to_json(filepath)
    print("Conversion process complete.")