# New test file addressing a known gap in utility function validation.
import pytest
from python_service.adapters.utils import parse_odds # Assuming a utility function exists or will be created

# This test codifies the expected behavior for a critical utility.
@pytest.mark.parametrize("input_odds, expected_decimal", [
    ("5/2", 2.5),
    ("10/1", 10.0),
    ("EVENS", 1.0),
    ("1/2", 0.5),
    ("SP", None), # Should handle non-fractional odds gracefully
    ("REF", None), # Should handle non-fractional odds gracefully
    ("", None),
    (None, None)
])
def test_parse_odds_edge_cases(input_odds, expected_decimal):
    """Tests the odds parsing utility with various common and edge-case formats."""
    if expected_decimal is not None:
        assert parse_odds(input_odds) == expected_decimal
    else:
        assert parse_odds(input_odds) is None