# Dedicated test suite for the TrifectaAnalyzer, resurrected and expanded.
import pytest
import datetime
from python_service.analyzer import TrifectaAnalyzer
from python_service.models import Race, Runner

@pytest.fixture
def analyzer():
    return TrifectaAnalyzer()

@pytest.fixture
def create_race(runners):
    return Race(
        id='test-race',
        venue='TEST',
        race_number=1,
        start_time=datetime.datetime.now(),
        runners=runners,
        source='test'
    )

def test_analyzer_name(analyzer):
    assert analyzer.name == "trifecta_analyzer"

# Test cases resurrected from legacy scorer and logic tests
def test_qualifies_with_exactly_three_runners(analyzer, create_race):
    runners = [
        Runner(number=1, name='A', odds='2/1', scratched=False),
        Runner(number=2, name='B', odds='3/1', scratched=False),
        Runner(number=3, name='C', odds='4/1', scratched=False)
    ]
    race = create_race(runners)
    assert analyzer.is_race_qualified(race) is True

def test_qualifies_with_more_than_three_runners(analyzer, create_race):
    runners = [
        Runner(number=1, name='A', odds='2/1', scratched=False),
        Runner(number=2, name='B', odds='3/1', scratched=False),
        Runner(number=3, name='C', odds='4/1', scratched=False),
        Runner(number=4, name='D', odds='5/1', scratched=False)
    ]
    race = create_race(runners)
    assert analyzer.is_race_qualified(race) is True

# New test cases for edge-case hardening
def test_rejects_with_fewer_than_three_runners(analyzer, create_race):
    runners = [
        Runner(number=1, name='A', odds='2/1', scratched=False),
        Runner(number=2, name='B', odds='3/1', scratched=False)
    ]
    race = create_race(runners)
    assert analyzer.is_race_qualified(race) is False

def test_rejects_if_scratched_runners_reduce_field_below_three(analyzer, create_race):
    runners = [
        Runner(number=1, name='A', odds='2/1', scratched=False),
        Runner(number=2, name='B', odds='3/1', scratched=False),
        Runner(number=3, name='C', odds='4/1', scratched=True) # Scratched
    ]
    race = create_race(runners)
    assert analyzer.is_race_qualified(race) is False

def test_handles_empty_runner_list(analyzer, create_race):
    race = create_race([])
    assert analyzer.is_race_qualified(race) is False

def test_handles_none_race_object(analyzer):
    assert analyzer.is_race_qualified(None) is False