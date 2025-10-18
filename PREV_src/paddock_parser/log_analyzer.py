import re
from collections import Counter
from typing import Dict

def analyze_log_file(log_file_path: str) -> Dict[str, int]:
    """
    Analyzes a log file to count occurrences of different log levels.

    Args:
        log_file_path: The path to the log file.

    Returns:
        A dictionary with log levels as keys and their counts as values.
        Returns an empty dictionary if the file cannot be read.
    """
    log_level_pattern = re.compile(r'\b(INFO|WARNING|ERROR|DEBUG|CRITICAL)\b')
    counts = Counter()

    try:
        with open(log_file_path, 'r') as f:
            for line in f:
                match = log_level_pattern.search(line)
                if match:
                    level = match.group(1)
                    counts[level] += 1
    except FileNotFoundError:
        return {}
    except Exception:
        return {}

    return dict(counts)
