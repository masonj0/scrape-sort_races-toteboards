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
    "python_service/adapters/betfair_greyhound_adapter.py",
    "python_service/adapters/racing_and_sports_greyhound_adapter.py",
    "python_service/adapters/at_the_races_adapter.py",
    "python_service/adapters/sporting_life_adapter.py",
    "python_service/adapters/timeform_adapter.py",
    "python_service/adapters/the_racing_api_adapter.py",
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
        # Simplified logic: Always read from the source path to ensure latest version.
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Store all content as raw strings for consistency.
            # The consumer of the JSON can parse the content if needed (e.g., for package.json).
            aggregated_data[file_path] = content
            print(f"Successfully processed file: {file_path}")
        else:
            print(f"Warning: Source file not found, skipping: {file_path}")
            continue

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