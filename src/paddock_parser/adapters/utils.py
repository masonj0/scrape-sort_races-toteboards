from datetime import datetime


def get_datetime_from_string(date_string: str) -> datetime:
    """
    Converts a date string to a datetime object.
    Supports formats:
    - 01 Sep 2025 17:45
    """
    try:
        return datetime.strptime(date_string, '%d %b %Y %H:%M')
    except ValueError:
        # Add other formats here if needed
        raise


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
                return 0.0
    try:
        return float(odds_str)
    except (ValueError, TypeError):
        return 0.0
