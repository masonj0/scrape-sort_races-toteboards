# python_service/utils/text.py
# Centralized text and name normalization utilities
import re
from typing import Optional


def clean_text(text: Optional[str]) -> Optional[str]:
    """Strips leading/trailing whitespace and collapses internal whitespace."""
    if not text:
        return None
    return " ".join(text.strip().split())


def normalize_venue_name(name: Optional[str]) -> Optional[str]:
    """
    Normalizes a UK or Irish racecourse name to a standard format.
    Handles common abbreviations and variations.
    """
    if not name:
        return None

    # Use a temporary variable for matching, but return the properly cased name
    cleaned_name_upper = clean_text(name).upper()

    VENUE_MAP = {
        "ASCOT": "Ascot",
        "AYR": "Ayr",
        "BANGOR-ON-DEE": "Bangor-on-Dee",
        "CATTERICK BRIDGE": "Catterick",
        "CHELMSFORD CITY": "Chelmsford",
        "EPSOM DOWNS": "Epsom",
        "FONTWELL": "Fontwell Park",
        "HAYDOCK": "Haydock Park",
        "KEMPTON": "Kempton Park",
        "LINGFIELD": "Lingfield Park",
        "NEWMARKET (ROWLEY)": "Newmarket",
        "NEWMARKET (JULY)": "Newmarket",
        "SANDOWN": "Sandown Park",
        "STRATFORD": "Stratford-on-Avon",
        "YARMOUTH": "Great Yarmouth",
        "CURRAGH": "Curragh",
        "DOWN ROYAL": "Down Royal",
    }

    # Check primary map first
    if cleaned_name_upper in VENUE_MAP:
        return VENUE_MAP[cleaned_name_upper]

    # Handle cases where the key is the desired output but needs to be mapped from a variation
    # e.g. CHELMSFORD maps to Chelmsford
    # Title case the cleaned name for a sensible default
    title_cased_name = clean_text(name).title()
    if title_cased_name in VENUE_MAP.values():
        return title_cased_name

    # Return the title-cased cleaned name as a fallback
    return title_cased_name


def normalize_course_name(name: str) -> str:
    if not name:
        return ""
    name = name.lower().strip()
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"[\s-]+", "_", name)
    return name
