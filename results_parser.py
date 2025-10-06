#!/usr/bin/env python3
# ==============================================================================
#  Fortuna Faucet: The Chart Parser (The Carpenter)
# ==============================================================================
# This module is responsible for parsing the complex, semi-structured text
# extracted from Equibase PDF race charts.
# ==============================================================================

import re
from typing import List

class ChartParser:
    """A sophisticated parser for Equibase PDF chart text."""

    def count_runners(self, chart_text: str) -> int:
        """
        Counts the number of runners in a race by parsing the 'Past Performance
        Running Line Preview' section, which is a reliable indicator of field size.
        """
        lines = chart_text.split('\n')
        in_running_line_section = False
        runner_count = 0

        for line in lines:
            # Heuristic to detect the start of the relevant section
            if 'Past Performance Running Line Preview' in line:
                in_running_line_section = True
                continue

            if in_running_line_section:
                # Stop if we hit a blank line or the next major section
                if not line.strip() or 'Trainers:' in line:
                    break

                # A valid runner line starts with a program number
                if re.match(r'^\d+', line.strip()):
                    runner_count += 1

        return runner_count

# --- Example Usage (for testing and demonstration) ---
if __name__ == '__main__':
    # This is a sample text block based on the 'Rosetta Stone' provided by the Project Lead
    SAMPLE_TEXT = ("""Last Raced Pgm Horse Name (Jockey) Wgt M/E PP Start 1/4 1/2 3/4 Str Fin Odds Comments
19Aug23 7ELP8 11 J J's Joker (Arrieta, Francisco) 120 L 11 1 41/2 51/2 51 21/2 11/2 7.08 4-3p,5w1/4,bid1/8,edgd
3Sep23 7KD7 2 Peek (Saez, Luis) 120 L 2 3 11/2 11/2 11 11 1/2 22 11.53 ins,dug in 2p1/8,bestd
15Sep23 1CD4 1 Game Warden (Gaffalione, Tyler) 120 L 1 2 52 41 41/2 31 3Neck 2.81* ins,aim btw1/4,lck bid
Total WPS Pool: $280,617
Pgm Horse Win Place Show
11 J J's Joker 16.16 8.00 5.78
2 Peek 10.80 6.22
1 Game Warden 3.78
Past Performance Running Line Preview
Pgm Horse Name Start 1/4 1/2 3/4 Str Fin
11 J J's Joker 1 42 1/2 53 1/2 52 1/2 21 1/2 11/2
2 Peek 3 11/2 11/2 11 11 1/2 21/2
1 Game Warden 2 53 42 1/2 42 32 32 1/2
4 Runningforjoy 9 75 1/2 64 63 1/2 53 42 3/4
5 Archie the Giza 7 96 1/2 87 85 1/2 64 1/2 54 1/4
8 Cafe Racer 4 21/2 21/2 31 43 65
9 Barnstorming 5 31 31 1/2 21 76 1/2 711 1/4
6 Cashmeup 8 65 75 1/2 74 87 1/2 811 1/2
10 Texas Pride 12 1214 1/2 1213 1/2 1114 1113 3/4 913
3 Active Duty 6 86 1/2 1110 1214 1/4 1013 1/2 1013 1/2
12 Surface to Air 10 108 99 97 1/2 911 1114
7 Dr Kringle 11 119 1/2 1010 108 1214 3/4 1217 3/4
Trainers: 11 - Hartman, Chris; 2 - Arnold, II, George; 1 - Joseph, Jr, Saffie; 4 - Tomlinson, Michael; 5 - Medina, Robert; 8 - Stall, Jr, Albert; 9 - Cox, Brad;
""")

    print("--- Testing ChartParser with sample data ---")
    parser = ChartParser()
    runner_count = parser.count_runners(SAMPLE_TEXT)

    print(f"Runner count found: {runner_count}")
    # Expected Output: 12
    assert runner_count == 12
    print("Test passed!")