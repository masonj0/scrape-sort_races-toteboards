#!/usr/bin/env python3
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

def parse_manifest(manifest_path: str) -> List[Dict]:
    """Parse manifest file (markdown or plain text) and extract file information."""
    entries = []

    with open(manifest_path, 'r') as f:
        content = f.read()

    # Split into lines and process
    lines = content.strip().split('\n')

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and headers
            continue

        # Extract file path and track name
        # Handle both markdown links and plain text
        file_info = extract_file_info(line)
        if file_info:
            entries.append(file_info)

    return entries

def extract_file_info(line: str) -> Optional[Dict]:
    """Extract file path and track information from a manifest line."""

    # Pattern 1: Markdown link format [track_name](path)
    md_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    md_match = re.search(md_pattern, line)

    if md_match:
        track_name = md_match.group(1)
        file_path = md_match.group(2)
    else:
        # Pattern 2: Plain text format (path or just filename)
        # Look for .html files
        if '.html' in line:
            file_path = line.strip()
            # Extract track name from filename
            track_name = extract_track_from_path(file_path)
        else:
            return None

    # Normalize the file path
    normalized_path = normalize_path(file_path)

    # Extract date and other metadata
    date_info = extract_date_from_path(normalized_path)

    return {
        'track': track_name,
        'path': normalized_path,
        'original_path': file_path,
        'date': date_info['date'] if date_info else None,
        'formatted_date': date_info['formatted'] if date_info else None,
        'filename': os.path.basename(normalized_path)
    }

def normalize_path(file_path: str) -> str:
    """Normalize file paths to handle both full and shortened versions."""

    # Remove any leading/trailing whitespace
    file_path = file_path.strip()

    # If it's already a full path starting with toteboard_scrapes, return as is
    if file_path.startswith('toteboard_scrapes/'):
        return file_path

    # If it starts with a date pattern (YYYY_MM_DD), prepend toteboard_scrapes/
    date_pattern = r'^\d{4}_\d{2}_\d{2}/'
    if re.match(date_pattern, file_path):
        return f'toteboard_scrapes/{file_path}'

    # If it's just a filename, try to find it in the directory structure
    if '/' not in file_path:
        # This is just a filename, we'll need context to place it
        return file_path

    return file_path

def extract_track_from_path(file_path: str) -> str:
    """Extract track name from file path."""

    filename = os.path.basename(file_path)

    # Remove .html extension
    name = filename.replace('.html', '')

    # Remove date prefix if present (YYYYMMDD_ or YYYY_MM_DD_)
    name = re.sub(r'^\d{8}_', '', name)
    name = re.sub(r'^\d{4}_\d{2}_\d{2}_', '', name)

    # Remove _data suffix if present
    name = re.sub(r'_data$', '', name)

    # Convert underscores to spaces and title case
    name = name.replace('_', ' ').title()

    return name

def extract_date_from_path(file_path: str) -> Optional[Dict]:
    """Extract date information from file path."""

    # Look for date in format YYYY_MM_DD
    date_pattern = r'(\d{4})_(\d{2})_(\d{2})'
    match = re.search(date_pattern, file_path)

    if match:
        year, month, day = match.groups()
        return {
            'date': f'{year}_{month}_{day}',
            'formatted': f'{year}-{month}-{day}',
            'year': year,
            'month': month,
            'day': day
        }

    # Look for date in format YYYYMMDD
    date_pattern2 = r'(\d{4})(\d{2})(\d{2})'
    match = re.search(date_pattern2, os.path.basename(file_path))

    if match:
        year, month, day = match.groups()
        return {
            'date': f'{year}_{month}_{day}',
            'formatted': f'{year}-{month}-{day}',
            'year': year,
            'month': month,
            'day': day
        }

    return None

def create_json_archive(manifest_files: List[str], output_file: str = 'archive.json'):
    """Create JSON archive from multiple manifest files."""

    all_entries = []

    for manifest_file in manifest_files:
        if not os.path.exists(manifest_file):
            print(f"Warning: Manifest file {manifest_file} not found, skipping...")
            continue

        print(f"Processing {manifest_file}...")
        entries = parse_manifest(manifest_file)

        # Add source manifest to each entry
        for entry in entries:
            entry['source_manifest'] = manifest_file

        all_entries.extend(entries)

    # Sort entries by date and track name
    all_entries.sort(key=lambda x: (x.get('date', ''), x.get('track', '')))

    # Group by date for better organization
    grouped = {}
    for entry in all_entries:
        date = entry.get('formatted_date', 'unknown')
        if date not in grouped:
            grouped[date] = []
        grouped[date].append(entry)

    # Create final structure
    archive = {
        'total_files': len(all_entries),
        'dates': list(grouped.keys()),
        'entries': all_entries,
        'grouped_by_date': grouped
    }

    # Write to JSON file
    with open(output_file, 'w') as f:
        json.dump(archive, f, indent=2)

    print(f"Created {output_file} with {len(all_entries)} entries")
    return archive

def main():
    """Main function to process manifest files."""

    # Look for all manifest files
    manifest_files = []

    # Check for numbered manifests
    for i in range(1, 10):
        for ext in ['.md', '.txt', '']:
            manifest_name = f'MANIFEST{i}{ext}'
            if os.path.exists(manifest_name):
                manifest_files.append(manifest_name)
                break

    # Check for non-numbered manifests
    for name in ['MANIFEST.md', 'MANIFEST.txt', 'MANIFEST']:
        if os.path.exists(name) and name not in manifest_files:
            manifest_files.append(name)

    if not manifest_files:
        print("No manifest files found!")
        return

    print(f"Found manifest files: {manifest_files}")

    # Create main archive
    archive = create_json_archive(manifest_files, 'archive.json')

    # Create a simplified index for web use
    simple_index = []
    for entry in archive['entries']:
        simple_index.append({
            'track': entry['track'],
            'date': entry.get('formatted_date', ''),
            'path': entry['path']
        })

    with open('index.json', 'w') as f:
        json.dump(simple_index, f, indent=2)

    print(f"Created index.json with simplified entries")

if __name__ == '__main__':
    main()