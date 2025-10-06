#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: The Chart Scraper
# ==============================================================================
# This script downloads and parses historical race result charts from Equibase PDF files.
# It forms the foundation of our Results Archive pillar.
# ==============================================================================

import requests
import pandas as pd
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from tabula import read_pdf
import os
import time
import pikepdf

class ChartScraper:
    """Orchestrates the downloading, decrypting, and parsing of Equibase PDF charts."""

    def __init__(self):
        self.download_dir = "results_archive"
        self.pdf_dir = os.path.join(self.download_dir, 'pdf')
        self.unlocked_pdf_dir = os.path.join(self.download_dir, 'pdf_unlocked')
        self.csv_dir = os.path.join(self.download_dir, 'csv')
        self.track_summary_url = "https://www.equibase.com/static/chart/summary/"
        self.pdf_url_pattern = (
            "http://www.equibase.com/premium/eqbPDFChartPlus.cfm?"
            "RACE={RACE}&BorP=P&TID={TID}&CTRY=USA&DT={DT}&DAY=D&STYLE=EQB"
        )
        self.races_to_check = range(1, 13)

    def _get_yesterday_date(self) -> tuple[str, str]:
        yesterday = datetime.now() - timedelta(days=1)
        return yesterday.strftime("%Y%m%d"), yesterday.strftime("%m/%d/%Y")

    def _get_yesterday_tracks(self, url_date_format: str) -> list[str]:
        full_url = f"{self.track_summary_url}{url_date_format}.html"
        print(f"-> Searching for tracks at: {full_url}")
        try:
            response = requests.get(full_url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching track summary page: {e}")
            return []

        soup = BeautifulSoup(response.content, 'lxml')
        track_codes = set()
        for a_tag in soup.find_all('a', href=True):
            if 'TID=' in a_tag['href']:
                try:
                    track_code = a_tag['href'].split('TID=')[1].split('&')[0]
                    track_codes.add(track_code)
                except IndexError:
                    continue

        unique_tracks = sorted(list(track_codes))
        print(f"-> Found {len(unique_tracks)} unique tracks: {unique_tracks}")
        return unique_tracks

    def _download_and_parse_chart(self, track_code: str, race_num: int, pdf_date_format: str):
        pdf_url = self.pdf_url_pattern.format(RACE=race_num, TID=track_code, DT=pdf_date_format)
        filename_base = f"{track_code}_{pdf_date_format.replace('/', '')}_R{race_num}"
        pdf_path = os.path.join(self.pdf_dir, f"{filename_base}.pdf")
        unlocked_pdf_path = os.path.join(self.unlocked_pdf_dir, f"{filename_base}_unlocked.pdf")
        csv_path = os.path.join(self.csv_dir, f"{filename_base}_scraped.csv")

        print(f"   - Attempting Race {race_num} ({track_code})...")
        try:
            pdf_response = requests.get(pdf_url, stream=True, timeout=15)
            content_type = pdf_response.headers.get('Content-Type', '')
            content_length = int(pdf_response.headers.get('Content-Length', 0))

            if 'application/pdf' not in content_type or content_length < 10000:
                print("     -> Not a valid PDF (race likely did not exist).")
                return

            with open(pdf_path, 'wb') as f:
                f.write(pdf_response.content)
            print(f"     -> Downloaded locked PDF to {pdf_path}")

        except requests.exceptions.RequestException as e:
            print(f"     -> Error downloading PDF: {e}")
            return

        # --- UNLOCKING STEP ---
        try:
            with pikepdf.open(pdf_path, allow_overwriting_input=True) as pdf:
                pdf.save(unlocked_pdf_path)
            print(f"     -> Saved unlocked PDF to {unlocked_pdf_path}")
        except Exception as e:
            print(f"     -> Failed to unlock PDF with pikepdf: {e}")
            return
        # --- END UNLOCKING ---

        try:
            tables = read_pdf(unlocked_pdf_path, pages='all', multiple_tables=True, lattice=True, silent=True)
            if not tables:
                print("     -> Tabula found no tables to extract from unlocked PDF.")
                return

            combined_df = pd.concat(tables, ignore_index=True)
            combined_df.to_csv(csv_path, index=False)
            print(f"     -> SUCCESSFULLY extracted {len(tables)} tables to {csv_path}")
        except Exception as e:
            print(f"     -> Error during Tabula PDF scraping: {e}")

    def run(self):
        os.makedirs(self.pdf_dir, exist_ok=True)
        os.makedirs(self.unlocked_pdf_dir, exist_ok=True)
        os.makedirs(self.csv_dir, exist_ok=True)
        print(f"Created/verified archive directory structure in: {self.download_dir}")

        url_date, pdf_date = self._get_yesterday_date()
        print(f"\\n--- Starting Equibase Chart Scraper for: {pdf_date} ---")

        tracks = self._get_yesterday_tracks(url_date)
        if not tracks:
            print("\\n*** No tracks found for yesterday. Halting. ***")
            return

        print("\\n--- Downloading, Unlocking, and Parsing Charts ---")
        for track in tracks:
            print(f"\\n[TRACK: {track}]")
            for race_num in self.races_to_check:
                self._download_and_parse_chart(track, race_num, pdf_date)
                time.sleep(1)

        print(f"\\n--- Scraper Finished! Check the '{self.csv_dir}' folder. ---")

if __name__ == "__main__":
    scraper = ChartScraper()
    scraper.run()