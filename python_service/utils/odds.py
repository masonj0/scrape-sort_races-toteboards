# Centralized odds parsing utility, created by Operation: The A+ Trifecta
from decimal import Decimal
from decimal import InvalidOperation
from typing import Optional
from typing import Union


def parse_odds_to_decimal(odds: Union[str, int, float, None]) -> Optional[Decimal]:
    """
    Parse various odds formats to Decimal for precise financial calculations.
    Handles fractional, decimal, and special cases ('EVS', 'SP', etc.).
    Returns None for unparseable or invalid values.
    """
    if odds is None:
        return None

    if isinstance(odds, (int, float)):
        return Decimal(str(odds))

    odds_str = str(odds).strip().upper()

    SPECIAL_CASES = {
        "EVS": Decimal("2.0"),
        "EVENS": Decimal("2.0"),
        "SP": None,
        "SCRATCHED": None,
        "SCR": None,
        "": None,
    }

    if odds_str in SPECIAL_CASES:
        return SPECIAL_CASES[odds_str]

    if "/" in odds_str:
        try:
            parts = odds_str.split("/")
            if len(parts) != 2:
                return None
            num, den = map(Decimal, parts)
            if den <= 0:
                return None
            return Decimal("1.0") + (num / den)
        except (ValueError, InvalidOperation):
            return None

    try:
        return Decimal(odds_str)
    except (ValueError, InvalidOperation):
        return None
