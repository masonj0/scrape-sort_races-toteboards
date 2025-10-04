import sys
import pytest

# Add the project root to the Python path
sys.path.insert(0, ".")

# Run pytest
if __name__ == "__main__":
    sys.exit(pytest.main(["tests/test_api.py"]))