from paddock_parser.adapters.base import BaseAdapterV3, NormalizedRace, NormalizedRunner
from bs4 import BeautifulSoup
import re
from typing import List

class EquibaseAdapter(BaseAdapterV3):
    """
    Adapter for equibase.com, parsing data from offline HTML samples.
    """
    SOURCE_ID = "equibase"

    def __init__(self, config=None):
        super().__init__(config)
        # Offline adapter

    async def fetch(self) -> List[NormalizedRace]:
        """This is an offline adapter and should not be fetched by the pipeline."""
        raise NotImplementedError("EquibaseAdapter is an offline adapter and does not support live fetching.")

    def parse_races(self, html_content: str) -> list[NormalizedRace]:
        """Public method to parse races, fulfilling the BaseAdapterV3 contract."""
        return self._parse_racecard(html_content)

    def _parse_racecard(self, html_content: str) -> list[NormalizedRace]:
        """Parses the HTML content of a single Equibase race card."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'lxml')

        track_name_tag = soup.select_one("div.track-info .track-name")
        track_name = track_name_tag.text.strip() if track_name_tag else "Unknown Track"

        race_number_tag = soup.select_one("div.race-number .selected a")
        race_number_str = race_number_tag.text.strip() if race_number_tag else "0"

        runners = []
        entries = soup.select("div.entry")
        for entry in entries:
            runner_number_tag = entry.select_one(".program-number")
            horse_name_tag = entry.select_one(".horse-name")
            jockey_name_tag = entry.select_one(".jockey-name")
            trainer_name_tag = entry.select_one(".trainer-name")

            is_scratched = "SCR" in entry.get("class", []) or "scratched" in entry.get("class", [])

            odds = None
            odds_tag = entry.select_one(".morning-line")
            if odds_tag and odds_tag.text.strip():
                try:
                    odds_parts = odds_tag.text.strip().split('/')
                    if len(odds_parts) == 2:
                        numerator, denominator = int(odds_parts[0]), int(odds_parts[1])
                        if denominator != 0:
                            odds = numerator / denominator
                except (ValueError, ZeroDivisionError):
                    odds = None

            if runner_number_tag and horse_name_tag and jockey_name_tag and trainer_name_tag:
                runners.append(NormalizedRunner(
                    name=horse_name_tag.text.strip(),
                    program_number=int(runner_number_tag.text.strip()),
                    jockey=jockey_name_tag.text.strip(),
                    trainer=trainer_name_tag.text.strip(),
                    scratched=is_scratched,
                    odds=odds
                ))

        if runners:
            race = NormalizedRace(
                race_id=f"{track_name.replace(' ', '')}-{race_number_str}",
                track_name=track_name,
                race_number=int(race_number_str),
                runners=runners,
                number_of_runners=len([r for r in runners if not r.scratched])
            )
            return [race]

        return []
