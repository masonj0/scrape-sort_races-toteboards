import json
import os

# This list is consolidated from MANIFEST2.md and MANIFEST3.md
ALL_FILES = [
    # MANIFEST2
    "python_service/__init__.py",
    "python_service/api.py",
    "python_service/engine.py",
    "python_service/models.py",
    "python_service/analyzer.py",
    "python_service/security.py",
    "python_service/adapters/__init__.py",
    "python_service/adapters/base.py",
    "python_service/adapters/utils.py",
    "python_service/adapters/betfair_adapter.py",
    "python_service/adapters/pointsbet_adapter.py",
    "python_service/adapters/racing_and_sports_adapter.py",
    "python_service/adapters/tvg_adapter.py",
    "python_service/adapters/harness_adapter.py",
    "python_service/adapters/greyhound_adapter.py",
    "web_platform/frontend/package.json",
    "web_platform/frontend/tailwind.config.ts",
    "web_platform/frontend/tsconfig.json",
    "web_platform/frontend/app/globals.css",
    "web_platform/frontend/app/layout.tsx",
    "web_platform/frontend/app/page.tsx",
    # MANIFEST3
    ".gitignore",
    "convert_to_json.py",
    "run_fortuna.bat",
    "setup_windows.bat",
    ".env",
    ".env.example",
    "python_service/requirements.txt",
    "README.md",
    "ARCHITECTURAL_MANDATE.md",
    "HISTORY.md",
    "STATUS.md",
    "WISDOM.md",
    "PROJECT_MANIFEST.md",
    "ROADMAP_APPENDICES.md",
    # Added during "The Great Correction"
    "python_service/config.py",
    "python_service/logging_config.py",
    "tests/conftest.py",
    "tests/test_analyzer.py",
    "tests/test_api.py",
    "tests/test_legacy_scenarios.py",
    "tests/adapters/test_greyhound_adapter.py",
    "tests/adapters/test_pointsbet_adapter.py",
]

aggregated_data = {}

print("Starting file aggregation...")

for file_path in ALL_FILES:
    content = None
    is_py = file_path.endswith('.py')

    try:
        if is_py:
            # For Python files, first attempt to read the content from the corresponding .json file in ReviewableJSON
            json_path = os.path.join("ReviewableJSON", file_path + ".json")
            if os.path.exists(json_path):
                with open(json_path, 'r', encoding='utf-8') as f:
                    try:
                        # The content is expected to be a JSON object with a 'content' key
                        data = json.load(f)
                        content = data.get('content')
                    except json.JSONDecodeError:
                        # If it's not a valid JSON object, read the raw text
                        f.seek(0)
                        content = f.read()
                print(f"Successfully processed PY file from JSON: {file_path}")
            else:
                # If the JSON backup doesn't exist, fall back to the raw .py file
                print(f"Info: JSON for PY file not found. Falling back to raw file: {file_path}")
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    print(f"Successfully processed raw PY file: {file_path}")
                else:
                    print(f"Warning: Raw source file also not found, skipping: {file_path}")
                    continue
        else:
            # For non-Python files, read from the source location
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"Successfully processed non-PY file: {file_path}")
            else:
                print(f"Warning: Source file not found, skipping: {file_path}")
                continue

        if isinstance(content, str):
            # For Python files, the content is raw source code and should not be parsed as JSON.
            # For other files (like package.json), we should attempt to parse them as JSON.
            if is_py:
                aggregated_data[file_path] = content
            else:
                try:
                    # Attempt to parse as JSON for non-python files
                    aggregated_data[file_path] = json.loads(content)
                except (json.JSONDecodeError, TypeError):
                    # If parsing fails, store as a raw string
                    aggregated_data[file_path] = content
        elif content is not None:
            aggregated_data[file_path] = content


    except Exception as e:
        print(f"ERROR processing file {file_path}: {e}")

# Write the aggregated data to the final JSON file
try:
    with open('FORTUNA_ALL.JSON', 'w', encoding='utf-8') as f:
        json.dump(aggregated_data, f, indent=4)
    print("\nSuccessfully created FORTUNA_ALL.JSON")
except Exception as e:
    print(f"\nERROR writing final JSON file: {e}")

print("\nAggregation complete.")