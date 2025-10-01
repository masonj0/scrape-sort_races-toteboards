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
    # This list is a direct reflection of the final manifest for the Council of AI Superbrains.
    # It includes all CORE and specified LEGACY files.
    files_to_convert = [
        # CORE Documentation
        "README.md",
        "ARCHITECTURAL_MANDATE.md",

        # CORE Frontend
        "web_platform/frontend/src/app/page.tsx",

        # CORE Backend
        "python_service/api.py",
        "python_service/engine.py",
        "python_service/adapters/__init__.py",
        "python_service/adapters/base.py",
        "python_service/adapters/betfair_adapter.py",
        "python_service/adapters/pointsbet_adapter.py",
        "python_service/adapters/tvg_adapter.py",
        "python_service/adapters/utils.py",
        "python_service/requirements.txt",

        # LEGACY Adapters (src/checkmate_v7)
        "src/checkmate_v7/adapters/AndWereOff.py",
        "src/checkmate_v7/adapters/Stablemates.py",
        "src/checkmate_v7/adapters/utils.py",

        # LEGACY Adapters (src/paddock_parser)
        "src/paddock_parser/adapters/atg_adapter.py",
        "src/paddock_parser/adapters/attheraces_adapter.py",
        "src/paddock_parser/adapters/betfair_data_scientist_adapter.py",
        "src/paddock_parser/adapters/equibase_adapter.py",
        "src/paddock_parser/adapters/fanduel_graphql_adapter.py",
        "src/paddock_parser/adapters/greyhound_recorder.py",
        "src/paddock_parser/adapters/pointsbet_adapter.py",
        "src/paddock_parser/adapters/racingandsports_adapter.py",
        "src/paddock_parser/adapters/racingpost_adapter.py",
        "src/paddock_parser/adapters/ras_adapter.py",
        "src/paddock_parser/adapters/skysports_adapter.py",
        "src/paddock_parser/adapters/timeform_adapter.py",
        "src/paddock_parser/adapters/twinspires_adapter.py",
        "src/paddock_parser/adapters/utils.py",

        # LEGACY Reviews
        "ReviewableJSON/attheraces_adapter.py.json",
        "ReviewableJSON/betfair_data_scientist_adapter.py.json",
        "ReviewableJSON/equibase.py.json",
        "ReviewableJSON/equibase_adapter.py.json",
        "ReviewableJSON/fanduel_graphql_adapter.py.json",
        "ReviewableJSON/greyhound_recorder.py.json",
        "ReviewableJSON/racingandsports_adapter.py.json",
        "ReviewableJSON/racingpost_adapter.py.json",
        "ReviewableJSON/skysports_adapter.py.json",
        "ReviewableJSON/timeform_adapter.py.json"
    ]

    print("Starting conversion based on the final manifest...")
    for filepath in files_to_convert:
        convert_file_to_json(filepath)
    print("Conversion process complete.")