# ==============================================================================
# == Centralized Adapter Utilities
# ==============================================================================
# This module provides shared, battle-tested functions for all adapters to use,
# ensuring consistency and adhering to the DRY principle.
# ==============================================================================

from typing import Union

def parse_odds(odds: Union[str, int, float]) -> float:
    """
    Parses various odds formats (e.g., fractional '10/1', decimal 11.0)
    into a standardized decimal float.

    Returns a default high odds value on failure to prevent crashes.
    """
    if isinstance(odds, (int, float)):
        return float(odds)

    if isinstance(odds, str):
        try:
            # Handle fractional odds (e.g., "10/1", "5/2")
            if "/" in odds:
                numerator, denominator = map(int, odds.split('/'))
                if denominator == 0: return 999.0
                return 1.0 + (numerator / denominator)

            # Handle "evens"
            if odds.lower() in ['evs', 'evens']:
                return 2.0

            # Handle simple decimal strings
            return float(odds)
        except (ValueError, TypeError):
            # Return a high, but valid, number for unparseable odds
            return 999.0

    return 999.0