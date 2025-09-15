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
    """Generates a diverse set of test data for development and testing."""
    from .models import Race, Runner
    return [
        # Thoroughbreds
        Race(discipline='Thoroughbred', track='Santa Anita', race_number=1, race_time='1:00 PM', runners=[Runner(name='Star Racer', odds=2.5), Runner(name='Gallop King', odds=3.0)]),
        Race(discipline='Thoroughbred', track='Churchill Downs', race_number=4, race_time='2:30 PM', runners=[Runner(name='Mint Julep', odds=1.8), Runner(name='Derby Dreamer', odds=4.5)]),
        # Greyhounds
        Race(discipline='Greyhound', track='Southland', race_number=8, race_time='7:00 PM', runners=[Runner(name='Rapid Fire', odds=3.0), Runner(name='Silver Bullet', odds=2.0)]),
        Race(discipline='Greyhound', track='Wheeling Island', race_number=10, race_time='8:15 PM', runners=[Runner(name='Box 1 Blitz', odds=4.0), Runner(name='Trap 6 Titan', odds=1.5)]),
        # Harness
        Race(discipline='Harness', track='Meadowlands', race_number=5, race_time='9:00 PM', runners=[Runner(name='Pacing Power', odds=2.2), Runner(name='Trotter Triumphant', odds=3.5)])
    ]
