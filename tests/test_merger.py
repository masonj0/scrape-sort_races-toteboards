import pytest

from paddock_parser.models import Race, Runner

# This is the function you will implement in src/paddock_parser/merger.py
# The test uses a local reference to the function, so we need to handle the import carefully
try:
    from paddock_parser.merger import smart_merge
except (ImportError, ModuleNotFoundError):
    # This allows the test file to be parsed even if the merger module doesn't exist yet
    def smart_merge(races):
        return races


# --- Test Cases for Operation SmartMerge ---

@pytest.fixture
def race_data():
    """ Provides a realistic list of races with duplicates to be merged. """
    race_1_sky = Race(race_id="Aintree_14:30", venue="Aintree", race_time="14:30", race_number=1, source="SkySports", is_handicap=False,
                      runners=[Runner(name="Horse A", odds="5/1"), Runner(name="Horse B", odds="10/1")])
    race_1_atr = Race(race_id="Aintree_14:30", venue="Aintree Racecourse", race_time="14:30", race_number=1, source="AtTheRaces", is_handicap=False,
                      runners=[Runner(name="Horse B", odds="12/1"), Runner(name="Horse C", odds="8/1")])
    race_2_unique = Race(race_id="Newmarket_15:00", venue="Newmarket", race_time="15:00", race_number=2, source="FanDuel", is_handicap=False,
                         runners=[Runner(name="Horse D", odds="2/1")])
    return [race_1_sky, race_1_atr, race_2_unique]

def test_deduplicates_races(race_data):
    """ SPEC: The function must reduce a list of races to only unique race_ids. """
    merged_races = smart_merge(race_data)
    assert len(merged_races) == 2

def test_merges_runners_and_respects_priority(race_data):
    """
    SPEC: The function must merge runner lists from duplicate races.
    - It must create a union of all unique runners.
    - If a runner exists in multiple sources, the odds from the HIGHER priority
      source must be used. Priority: FanDuel > SkySports > AtTheRaces.
    """
    merged_races = smart_merge(race_data)
    merged_aintree_race = next(r for r in merged_races if r.race_id == "Aintree_14:30")

    assert len(merged_aintree_race.runners) == 3

    runner_names = {r.name for r in merged_aintree_race.runners}
    assert "Horse A" in runner_names
    assert "Horse B" in runner_names
    assert "Horse C" in runner_names

    horse_b = next(r for r in merged_aintree_race.runners if r.name == "Horse B")
    assert horse_b.odds == "10/1"

def test_tracks_provenance_correctly(race_data):
    """
    SPEC: The final merged race must have a 'sources' list containing the names
    of all contributing adapters, sorted by priority.
    """
    merged_races = smart_merge(race_data)

    merged_aintree_race = next(r for r in merged_races if r.race_id == "Aintree_14:30")
    assert merged_aintree_race.sources == ["SkySports", "AtTheRaces"]

    unique_newmarket_race = next(r for r in merged_races if r.race_id == "Newmarket_15:00")
    assert unique_newmarket_race.sources == ["FanDuel"]

def test_prioritizes_metadata_from_best_source(race_data):
    """ SPEC: The top-level metadata (like 'venue') of the final merged race
    should come from the highest-priority source. """
    merged_races = smart_merge(race_data)
    merged_aintree_race = next(r for r in merged_races if r.race_id == "Aintree_14:30")
    assert merged_aintree_race.venue == "Aintree"

def test_handles_no_duplicates():
    """ SPEC: If no duplicates are present, the output should be logically identical to the input. """
    races = [
        Race(race_id="R1", venue="V1", race_time="T1", race_number=1, source="S1", is_handicap=False, runners=[]),
        Race(race_id="R2", venue="V2", race_time="T2", race_number=2, source="S2", is_handicap=False, runners=[]),
    ]
    merged_races = smart_merge(races)
    assert len(merged_races) == 2
    assert merged_races[0].sources == ["S1"]
    assert merged_races[1].sources == ["S2"]
