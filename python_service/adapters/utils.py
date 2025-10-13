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
        odds = odds.strip().upper()
        if not odds or odds in ['SP', 'REF']:
            return None
        try:
            if "/" in odds:
                numerator, denominator = map(int, odds.split('/'))
                if denominator == 0:
                    return None
                return numerator / denominator
            if odds in ['EVS', 'EVENS']:
                return 1.0
            return float(odds)
        except (ValueError, TypeError):
            return None
    return None


# --- Track Name Normalization (Resurrected from attic/checkmate_app.py) ---
TRACK_ALIASES = {
    'Aqueduct': 'AQU', 'Belmont Park': 'BEL', 'Churchill Downs': 'CD', 'Del Mar': 'DMR',
    'Fair Grounds': 'FG', 'Gulfstream Park': 'GP', 'Keeneland': 'KEE', 'Laurel Park': 'LRL',
    'Monmouth Park': 'MTH', 'Oaklawn Park': 'OP', 'Pimlico': 'PIM', 'Saratoga': 'SAR',
    'Santa Anita Park': 'SA', 'Tampa Bay Downs': 'TAM', 'Woodbine': 'WO', 'Turfway Park': 'TP'
}
def normalize_track_name(track_name: str) -> str:
    """Normalizes a track name using a dictionary of known aliases."""
    return TRACK_ALIASES.get(track_name.strip(), track_name.strip())


def normalize_course_name(name: str) -> str:
    import re
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9\s-]', '', name)
    name = re.sub(r'[\s-]+', '_', name)
    return name