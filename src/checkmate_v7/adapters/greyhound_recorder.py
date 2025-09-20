import json
from datetime import datetime
from typing import List, Optional, Dict, Any

from bs4 import BeautifulSoup

from ..base import BaseAdapterV3, NormalizedRace, NormalizedRunner


class GreyhoundRecorderAdapter(BaseAdapterV3):
    """
    Adapter for greyhoundrecorder.co.uk racecards.
    Parses data from a JSON blob embedded in the HTML.
    """
    SOURCE_ID = "greyhoundrecorder"

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)

    async def fetch(self) -> List[NormalizedRace]:
        """This is an offline adapter and should not be fetched by the pipeline."""
        raise NotImplementedError("GreyhoundRecorderAdapter is an offline adapter and does not support live fetching.")

    def parse_races(self, html_content: str) -> List[NormalizedRace]:
        """Public method to parse races, fulfilling the BaseAdapterV3 contract."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'lxml')
        race_data_json = self._extract_race_data_json(soup)
        if not race_data_json:
            return []

        return self._parse_races_from_json(race_data_json)

    def _extract_race_data_json(self, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Extracts the JSON data blob from the page's script tags."""
        script_tag = soup.find('script', {'id': '__NEXT_DATA__'})
        if script_tag and script_tag.string:
            try:
                return json.loads(script_tag.string)
            except json.JSONDecodeError:
                return None
        return None

    def _parse_races_from_json(self, race_data: Dict[str, Any]) -> List[NormalizedRace]:
        """Parses all race information from the main JSON data object."""
        races = []
        try:
            tracks_data = race_data['props']['pageProps']['tracks']
            for track in tracks_data:
                track_name = track.get('name')
                for race_info in track.get('races', []):
                    runners = []
                    for runner_info in race_info.get('traps', []):
                        runner_name = runner_info.get('dog', {}).get('name')
                        if not runner_name:  # Skip empty traps
                            continue

                        runners.append(
                            NormalizedRunner(
                                name=runner_name,
                                program_number=runner_info.get('trap'),
                                jockey=None,  # Not applicable for greyhounds
                                trainer=runner_info.get('trainer', {}).get('name')
                            )
                        )

                    post_time_str = race_info.get('time')
                    post_time = self._parse_datetime(post_time_str) if post_time_str else None

                    races.append(
                        NormalizedRace(
                            race_id=str(race_info.get('id')),
                            track_name=track_name,
                            race_number=race_info.get('race'),
                            post_time=post_time,
                            race_type=None,  # Not available in data
                            number_of_runners=len(runners),
                            runners=runners
                        )
                    )
        except (KeyError, TypeError):
            # Handle cases where the JSON structure is not as expected
            return []

        return races

    def _parse_datetime(self, dt_string: str) -> Optional[datetime]:
        """Parses a datetime string like '2023-10-21T10:31:00.000Z'."""
        try:
            # Strip the 'Z' and milliseconds for compatibility
            dt_string = dt_string.split('.')[0]
            return datetime.fromisoformat(dt_string)
        except (ValueError, TypeError):
            return None
