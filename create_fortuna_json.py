#!/usr/bin/env python3
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set

def parse_fortuna_manifest(manifest_path: str) -> List[Dict]:
    """Parse Fortuna-specific manifest entries."""
    entries = []

    with open(manifest_path, 'r') as f:
        content = f.read()

    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        # Check if this is a Fortuna-related entry
        if 'fortuna' in line.lower() or 'FORTUNA' in line:
            entry = extract_fortuna_info(line)
            if entry:
                entries.append(entry)

    return entries

def extract_fortuna_info(line: str) -> Optional[Dict]:
    """Extract Fortuna-specific information from a line."""

    # Handle markdown format
    md_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    md_match = re.search(md_pattern, line)

    if md_match:
        display_name = md_match.group(1)
        file_path = md_match.group(2)
    else:
        # Plain text format
        if '.html' in line:
            file_path = line.strip()
            display_name = extract_display_name(file_path)
        else:
            return None

    # Only process Fortuna files
    if 'fortuna' not in file_path.lower():
        return None

    # Normalize path
    normalized_path = normalize_fortuna_path(file_path)

    # Extract metadata
    metadata = extract_fortuna_metadata(normalized_path)

    return {
        'display_name': display_name,
        'path': normalized_path,
        'original_path': file_path,
        'filename': os.path.basename(normalized_path),
        **metadata
    }

def normalize_fortuna_path(file_path: str) -> str:
    """Normalize Fortuna file paths."""

    file_path = file_path.strip()

    # Handle full paths
    if file_path.startswith('toteboard_scrapes/'):
        return file_path

    # Handle date-prefixed paths
    date_pattern = r'^\d{4}_\d{2}_\d{2}/'
    if re.match(date_pattern, file_path):
        return f'toteboard_scrapes/{file_path}'

    # Handle fortuna-specific subdirectories
    if file_path.startswith('fortuna/'):
        # Try to find the appropriate date directory
        return f'toteboard_scrapes/{file_path}'

    return file_path

def extract_display_name(file_path: str) -> str:
    """Extract a display name from the file path."""

    filename = os.path.basename(file_path)
    name = filename.replace('.html', '')

    # Remove date prefixes
    name = re.sub(r'^\d{8}_', '', name)
    name = re.sub(r'^\d{4}_\d{2}_\d{2}_', '', name)

    # Clean up Fortuna-specific naming
    name = name.replace('FORTUNA_', '').replace('fortuna_', '')
    name = name.replace('_', ' ').title()

    return name

def extract_fortuna_metadata(file_path: str) -> Dict:
    """Extract Fortuna-specific metadata from the file path."""

    metadata = {}

    # Extract date
    date_match = re.search(r'(\d{4})_(\d{2})_(\d{2})', file_path)
    if date_match:
        year, month, day = date_match.groups()
        metadata['date'] = f'{year}-{month}-{day}'
        metadata['year'] = int(year)
        metadata['month'] = int(month)
        metadata['day'] = int(day)

        # Create timestamp
        try:
            dt = datetime(int(year), int(month), int(day))
            metadata['timestamp'] = dt.isoformat()
        except:
            pass

    # Extract race number if present
    race_match = re.search(r'[Rr]ace[_\\s]?(\d+)', file_path)
    if race_match:
        metadata['race_number'] = int(race_match.group(1))

    # Determine file type
    if 'results' in file_path.lower():
        metadata['type'] = 'results'
    elif 'entries' in file_path.lower():
        metadata['type'] = 'entries'
    elif 'changes' in file_path.lower():
        metadata['type'] = 'changes'
    else:
        metadata['type'] = 'data'

    return metadata

def create_fortuna_archive(manifest_files: List[str], output_file: str = 'fortuna.json'):
    """Create Fortuna-specific JSON archive."""

    all_entries = []
    processed_paths = set()  # Track processed files to avoid duplicates

    for manifest_file in manifest_files:
        if not os.path.exists(manifest_file):
            print(f"Warning: Manifest file {manifest_file} not found, skipping...")
            continue

        print(f"Processing {manifest_file} for Fortuna entries...")

        # First, try to parse as Fortuna-specific
        entries = parse_fortuna_manifest(manifest_file)

        # If no Fortuna entries found, do a general parse and filter
        if not entries:
            with open(manifest_file, 'r') as f:
                content = f.read()

            lines = content.strip().split('\\n')
            for line in lines:
                if 'fortuna' in line.lower() or 'FORTUNA' in line:
                    entry = extract_fortuna_info(line)
                    if entry:
                        entries.append(entry)

        # Add source and check for duplicates
        for entry in entries:
            if entry['path'] not in processed_paths:
                entry['source_manifest'] = manifest_file
                all_entries.append(entry)
                processed_paths.add(entry['path'])

    # Sort entries by date and race number
    all_entries.sort(key=lambda x: (
        x.get('date', '9999-99-99'),
        x.get('race_number', 999),
        x.get('display_name', '')
    ))

    # Group by date
    grouped = {}
    for entry in all_entries:
        date = entry.get('date', 'unknown')
        if date not in grouped:
            grouped[date] = {
                'date': date,
                'races': []
            }
        grouped[date]['races'].append(entry)

    # Create archive structure
    archive = {
        'track': 'Fortuna',
        'total_files': len(all_entries),
        'date_range': {
            'start': min((e.get('date', '9999') for e in all_entries), default=''),
            'end': max((e.get('date', '0000') for e in all_entries), default='')
        },
        'dates': sorted(grouped.keys()),
        'entries': all_entries,
        'grouped_by_date': grouped,
        'metadata': {
            'created': datetime.now().isoformat(),
            'version': '2.0'
        }
    }

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(archive, f, indent=2)

    print(f"Created {output_file} with {len(all_entries)} Fortuna entries")

    # Also create a simplified index
    simple_index = []
    for entry in all_entries:
        simple_index.append({
            'name': entry['display_name'],
            'date': entry.get('date', ''),
            'race': entry.get('race_number', ''),
            'type': entry.get('type', 'data'),
            'path': entry['path']
        })

    with open('fortuna_index.json', 'w') as f:
        json.dump(simple_index, f, indent=2)

    print(f"Created fortuna_index.json with simplified entries")

    return archive

def main():
    """Main function to process Fortuna entries."""

    # Find all manifest files
    manifest_files = []

    # Check for specific manifests mentioned
    for name in ['MANIFEST2.md', 'MANIFEST3.md']:
        if os.path.exists(name):
            manifest_files.append(name)

    # Also check for other manifest files
    for i in range(1, 10):
        for ext in ['.md', '.txt', '']:
            manifest_name = f'MANIFEST{i}{ext}'
            if os.path.exists(manifest_name) and manifest_name not in manifest_files:
                manifest_files.append(manifest_name)

    # Check for base MANIFEST files
    for name in ['MANIFEST.md', 'MANIFEST.txt', 'MANIFEST']:
        if os.path.exists(name) and name not in manifest_files:
            manifest_files.append(name)

    if not manifest_files:
        print("No manifest files found!")
        return

    print(f"Found manifest files: {manifest_files}")

    # Create Fortuna archive
    archive = create_fortuna_archive(manifest_files, 'fortuna.json')

    # Print summary
    print("\\nSummary:")
    print(f"Total Fortuna entries: {archive['total_files']}")
    print(f"Date range: {archive['date_range']['start']} to {archive['date_range']['end']}")
    print(f"Number of dates: {len(archive['dates'])}")

if __name__ == '__main__':
    main()