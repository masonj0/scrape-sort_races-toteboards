from bs4 import BeautifulSoup
from paddock_parser.models.race import NormalizedRace, RaceStatus
from paddock_parser.models.runner import NormalizedRunner, RunnerStatus
from paddock_parser.parsers.base import BaseAdapterV3
import re
from datetime import datetime

class EquibaseAdapter(BaseAdapterV3):
    SOURCE_NAME = "equibase"

    def parse_races(self, html: str) -> list[NormalizedRace]:
        soup = BeautifulSoup(html, "html.parser")
        races = []

        track_id = self._parse_track_id(soup)
        race_date = self._parse_race_date(soup)

        race_rows = soup.select("table#entryRaces tbody tr")

        for row in race_rows:
            cells = row.find_all("td")
            if not cells:
                continue

            race_number_anchor = cells[0].find("a")
            if not race_number_anchor:
                continue

            race_number = race_number_anchor.text.strip()
            purse = self._parse_purse(cells[1].text.strip())
            race_type = cells[2].text.strip()
            distance = cells[3].text.strip()
            surface = cells[4].text.strip()
            starters = int(cells[5].text.strip())

            # Since we don't have runner details, we'll create placeholder runners
            runners = [NormalizedRunner(source_id=str(i+1), name=f"Runner {i+1}") for i in range(starters)]

            races.append(
                NormalizedRace(
                    race_id=f"{track_id}-{race_date}-{race_number}",
                    source_id=f"{track_id}-{race_date}-{race_number}",
                    source_name=self.SOURCE_NAME,
                    name=race_type,
                    status=RaceStatus.OPEN,
                    purse=purse,
                    distance=distance,
                    surface=surface,
                    runners=runners,
                )
            )

        return races

    def _parse_track_id(self, soup):
        track_name_element = soup.find("h1", id="pageHeader")
        if track_name_element:
            track_name = track_name_element.text.strip().split(" ")[0]
            # This is a hack, we need a proper track code mapping
            if "Saratoga" in track_name:
                return "SAR"
        return "UNKNOWN"

    def _parse_race_date(self, soup):
        date_element = soup.find("div", class_="breadcrumbs")
        if date_element:
            date_anchors = date_element.find_all("a")
            if len(date_anchors) > 2:
                date_text = date_anchors[2].text.strip() # "August 22, 2025"
                try:
                    # Attempt to parse the date string
                    dt_object = datetime.strptime(date_text, "%B %d, %Y")
                    return dt_object.strftime("%Y-%m-%d")
                except (ValueError, IndexError):
                    pass
        # Fallback for mobile view
        mobile_header = soup.find("h1", id="pageHeaderMobile")
        if mobile_header:
            # "Saratoga | Aug 22, 2025"
            parts = mobile_header.text.split("|")
            if len(parts) > 1:
                date_text = parts[1].strip()
                try:
                    dt_object = datetime.strptime(date_text, "%b %d, %Y")
                    return dt_object.strftime("%Y-%m-%d")
                except ValueError:
                    pass

        return "UNKNOWN-DATE"

    def _parse_purse(self, purse_string: str) -> int:
        return int(re.sub(r'[$,]', '', purse_string))

    def _parse_odds(self, odds_string: str) -> float:
        if "/" in odds_string:
            numerator, denominator = odds_string.split("/")
            return float(numerator) / float(denominator)
        return float(odds_string)
