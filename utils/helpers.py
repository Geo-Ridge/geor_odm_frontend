# -*- coding: utf-8 -*-
"""Helper utilities for ODM Frontend."""

import os
import re


def is_projection_line(line):
    """Check if a line looks like a projection definition."""
    line = line.strip()
    if line.startswith('+proj=') or line.startswith('EPSG:'):
        return True
    if 'UTM' in line.upper() and ('zone' in line.lower() or '+' in line):
        return True
    return False


def parse_task_id(task_text):
    """Extract task UUID from task list item text."""
    # Try format: "Name (ID: uuid) - Status"
    if 'ID: ' in task_text:
        parts = task_text.split('ID: ')
        if len(parts) > 1:
            after_id = parts[1]
            bracket_parts = after_id.split(')')
            if bracket_parts:
                task_id = bracket_parts[0].strip()
                if task_id and task_id != 'N/A':
                    return task_id

    # Fallback: regex for UUID
    uuid_match = re.search(
        r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}',
        task_text
    )
    if uuid_match:
        return uuid_match.group(0)

    return None


def format_processing_time(milliseconds):
    """Format processing time from milliseconds to MM:SS."""
    if milliseconds <= 0:
        return ""
    minutes = milliseconds // (1000 * 60)
    seconds = (milliseconds // 1000) % 60
    return f" ({int(minutes):02d}:{int(seconds):02d})"


def find_image_path(filename, image_paths):
    """Find full path for a filename in the image paths list."""
    for path in image_paths:
        if os.path.basename(path) == filename:
            return path
    return None


def validate_image_paths(image_paths):
    """Validate image paths and return list of existing files."""
    valid = []
    missing = []
    for path in image_paths:
        if os.path.exists(path):
            valid.append(path)
        else:
            missing.append(path)
    return valid, missing


def get_status_text(status_code):
    """Convert status code to readable text."""
    status_map = {
        10: 'QUEUED',
        20: 'RUNNING',
        30: 'FAILED',
        40: 'COMPLETED',
        50: 'CANCELED'
    }
    return status_map.get(status_code, f'UNKNOWN({status_code})')
