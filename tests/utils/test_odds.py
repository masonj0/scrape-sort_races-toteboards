# tests/utils/test_odds.py
import pytest
from decimal import Decimal
from python_service.utils.odds import parse_odds_to_decimal

@pytest.mark.parametrize("input_odds, expected_decimal", [
    ("5/2", Decimal("3.5")),      # 2.5 + 1 stake
    ("10/1", Decimal("11.0")),     # 10.0 + 1 stake
    ("EVENS", Decimal("2.0")),     # 1.0 + 1 stake
    ("EVS", Decimal("2.0")),       # 1.0 + 1 stake
    ("1/2", Decimal("1.5")),       # 0.5 + 1 stake
    ("2.5", Decimal("2.5")),       # Handles decimal strings
    (3.5, Decimal("3.5")),         # Handles float input
    (10, Decimal("10")),           # Handles int input
    ("SP", None),                  # Should handle non-fractional odds gracefully
    ("SCR", None),                 # Should handle scratched runners
    ("REF", None),                 # Should handle other non-numeric values
    ("", None),
    (None, None)
])
def test_parse_odds_to_decimal(input_odds, expected_decimal):
    """Tests the new centralized odds parsing utility with various formats."""
    assert parse_odds_to_decimal(input_odds) == expected_decimal
