def _convert_odds_to_float(odds_str: str) -> float:
    """Converts odds string to a float. Handles 'EVS' and fractions."""
    if isinstance(odds_str, str):
        odds_str = odds_str.strip().upper()
        if odds_str == 'EVS':
            return 2.0
        if '/' in odds_str:
            try:
                num, den = map(int, odds_str.split('/'))
                return (num / den) + 1.0
            except (ValueError, ZeroDivisionError):
                return float('inf')
    return float('inf')
