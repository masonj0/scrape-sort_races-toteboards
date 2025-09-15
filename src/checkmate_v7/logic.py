"""
Checkmate V7: `logic.py` - THE BRAIN
"""
from typing import Dict

def quantitative_scoring(race_data: Dict) -> float:
    """Placeholder for quantitative scoring logic."""
    return 7.5

def qualitative_analysis_mock(race_data: Dict) -> Dict:
    """Placeholder for qualitative analysis (LLM call)."""
    return {"probability_multiplier": 1.0}

def apply_final_qualification(score: float, odds: float) -> bool:
    """Placeholder for final qualification logic."""
    return score > 7.0

def get_test_data():
    """Generates test data for development and testing."""
    # This function is moved from the old RaceDataFetcher for better separation of concerns.
    from .models import Race, Runner # Local import to avoid circular dependency issues
    return [
        Race(
            discipline='Thoroughbred',
            track='Test Park',
            race_number=1,
            race_time='2:15 PM',
            runners=[
                Runner(name='Alpha', odds=1.5), Runner(name='Bravo', odds=3.8),
                Runner(name='Charlie', odds=5.0), Runner(name='Delta', odds=7.0),
                Runner(name='Eagle', odds=10.0)
            ]
        ),
        Race(
            discipline='Thoroughbred',
            track='Demo Downs',
            race_number=3,
            race_time='3:05 PM',
            runners=[
                Runner(name='Echo', odds=0.8), Runner(name='Foxtrot', odds=2.8),
                Runner(name='Golf', odds=9.0)
            ]
        )
    ]
