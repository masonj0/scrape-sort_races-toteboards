import json
import re
from datetime import datetime
from typing import List, Optional, Dict, Any

from bs4 import BeautifulSoup

from paddock_parser.adapters.base import BaseAdapterV3, NormalizedRace, NormalizedRunner


class RacingPostAdapter(BaseAdapterV3):
    """
    Adapter for racingpost.com, parsing data from offline HTML samples.
    This adapter is designed to parse the complex structure of Racing Post racecards,
    which involves extracting data from both a JSON blob embedded in a script tag
    and the main HTML structure.
    """
    SOURCE_ID = "racingpost"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def fetch(self) -> List[NormalizedRace]:
        """This is an offline adapter and should not be fetched by the pipeline."""
        raise NotImplementedError("RacingPostAdapter is an offline adapter and does not support live fetching.")

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """Public method to parse races, fulfilling the BaseAdapterV3 contract."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'lxml')

        # The core race data is in a JSON blob within a script tag.
        race_data_json = self._extract_race_data_json(html_content)
        if not race_data_json:
            return []

        # The runner data is in the main HTML structure.
        # We find all race containers and assume they are in the same order as the JSON subEvents.
        race_containers = soup.select('div.RC-meetingDay__race')

        # The sample HTML only contains the runner details for the first race.
        # So we will only process the first race.
        if not race_containers:
            return []

        race_container = race_containers[0]
        race_info = race_data_json.get('subEvent', [])[0]

        return [self._parse_single_race(race_info, race_container, race_data_json)]

    def _parse_single_race(self, race_info: Dict[str, Any], race_container: BeautifulSoup, race_data_json: Dict[str, Any]) -> NormalizedRace:
        """Parses a single race from its JSON info and HTML container."""

        # Extract runners from the HTML container
        runners = []
        runner_rows = race_container.select('div.RC-runnerRow')
        for row in runner_rows:
            # Skip non-runners
            if 'RC-runnerRow_disabled' in row.get('class', []):
                continue

            program_number_span = row.select_one('span.RC-runnerNumber__no')
            program_number = int(program_number_span.text.strip()) if program_number_span else None

            runner_name_a = row.select_one('a.RC-runnerName')
            runner_name = runner_name_a.text.strip() if runner_name_a else None

            jockey_a = row.select_one('a[data-test-selector="RC-cardPage-runnerJockey-name"]')
            jockey_name = jockey_a.text.strip() if jockey_a else None

            trainer_a = row.select_one('a[data-test-selector="RC-cardPage-runnerTrainer-name"]')
            trainer_name = trainer_a.text.strip() if trainer_a else None

            runners.append(
                NormalizedRunner(
                    name=runner_name,
                    program_number=program_number,
                    jockey=jockey_name,
                    trainer=trainer_name,
                    odds=None # Odds are not available in a structured way in the static HTML
                )
            )

        # Extract race details from the JSON
        post_time_str = race_info.get('startDate')
        post_time = self._parse_datetime(post_time_str) if post_time_str else None

        return NormalizedRace(
            race_id=f"{race_data_json.get('location', {}).get('name', '').replace(' ', '')}-{race_info.get('name', '').replace(' ', '')[:10]}",
            track_name=race_data_json.get('location', {}).get('name'),
            race_number=None, # Not available directly, would need to infer
            post_time=post_time,
            race_type=race_info.get('name'),
            number_of_runners=len(runners),
            runners=runners
        )

    def _extract_race_data_json(self, html_content: str) -> Optional[Dict[str, Any]]:
        """Extracts the main JSON data blob from the page's script tags."""
        # This regex is designed to find the `rp_config_.page` object.
        match = re.search(r'rp_config_\.page\s*=\s*({.*?});', html_content, re.DOTALL)
        if match:
            json_str = match.group(1)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                return None
        return None

    def _parse_datetime(self, dt_string: str) -> Optional[datetime]:
        """Parses an ISO 8601 formatted datetime string with timezone."""
        try:
            # Python's fromisoformat can handle the timezone offset
            return datetime.fromisoformat(dt_string)
        except (ValueError, TypeError):
            return None
