#!/usr/bin/env python3
"""
Migration script to update video metadata files with timezone information.

This script converts naive datetime strings in JSON files to timezone-aware
datetime strings (UTC format).

Run this after upgrading to the timezone-aware version.
"""

import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo

# Configuration
VIDEO_DIRECTORY = "videos"
TIMEZONE = "Europe/Berlin"  # Assume old timestamps were in this timezone
DRY_RUN = False  # Set to True to see what would be changed without making changes


def migrate_json_file(filepath: str) -> bool:
    """
    Migrate a single JSON file to use timezone-aware timestamps.

    Args:
        filepath: Path to the JSON file

    Returns:
        True if migration was needed and performed, False otherwise
    """
    try:
        # Read the file
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Check if migration is needed
        needs_migration = False

        # Check start_time
        start_time_str = data.get("start_time", "")
        if start_time_str and "+" not in start_time_str and "Z" not in start_time_str:
            needs_migration = True

        # Check end_time
        end_time_str = data.get("end_time")
        if end_time_str and "+" not in end_time_str and "Z" not in end_time_str:
            needs_migration = True

        if not needs_migration:
            print(f"  ✓ {filepath} - Already migrated, skipping")
            return False

        # Perform migration
        local_tz = ZoneInfo(TIMEZONE)

        # Migrate start_time
        if start_time_str:
            start_dt = datetime.fromisoformat(start_time_str)
            if start_dt.tzinfo is None:
                # Add timezone info (assume local timezone) and convert to UTC
                start_dt = start_dt.replace(tzinfo=local_tz)
                data["start_time"] = start_dt.isoformat()

        # Migrate end_time
        if end_time_str:
            end_dt = datetime.fromisoformat(end_time_str)
            if end_dt.tzinfo is None:
                # Add timezone info (assume local timezone) and convert to UTC
                end_dt = end_dt.replace(tzinfo=local_tz)
                data["end_time"] = end_dt.isoformat()

        # Write back to file
        if not DRY_RUN:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  ✓ {filepath} - Migrated successfully")
        else:
            print(f"  ○ {filepath} - Would migrate (dry run)")
            print(f"    Old start_time: {start_time_str}")
            print(f"    New start_time: {data['start_time']}")
            if end_time_str:
                print(f"    Old end_time: {end_time_str}")
                print(f"    New end_time: {data['end_time']}")

        return True

    except Exception as e:
        print(f"  ✗ {filepath} - Error: {e}")
        return False


def main():
    """Main migration function"""
    print("=" * 70)
    print("Video Metadata Timezone Migration")
    print("=" * 70)
    print(f"Video directory: {VIDEO_DIRECTORY}")
    print(f"Assumed timezone for old data: {TIMEZONE}")
    print(f"Dry run: {'YES (no changes will be made)' if DRY_RUN else 'NO (files will be updated)'}")
    print("=" * 70)
    print()

    if not os.path.exists(VIDEO_DIRECTORY):
        print(f"Error: Directory '{VIDEO_DIRECTORY}' does not exist")
        return

    # Find all JSON files
    json_files = [f for f in os.listdir(VIDEO_DIRECTORY) if f.endswith('.json')]

    if not json_files:
        print("No JSON files found in video directory")
        return

    print(f"Found {len(json_files)} JSON file(s)")
    print()

    # Migrate each file
    migrated_count = 0
    skipped_count = 0
    error_count = 0

    for filename in sorted(json_files):
        filepath = os.path.join(VIDEO_DIRECTORY, filename)
        try:
            if migrate_json_file(filepath):
                migrated_count += 1
            else:
                skipped_count += 1
        except Exception as e:
            print(f"  ✗ {filepath} - Unexpected error: {e}")
            error_count += 1

    # Summary
    print()
    print("=" * 70)
    print("Migration Summary")
    print("=" * 70)
    print(f"Total files: {len(json_files)}")
    print(f"Migrated: {migrated_count}")
    print(f"Skipped (already migrated): {skipped_count}")
    print(f"Errors: {error_count}")
    print()

    if DRY_RUN and migrated_count > 0:
        print("⚠ This was a DRY RUN - no changes were made")
        print("⚠ Set DRY_RUN = False in the script to perform the actual migration")
    elif migrated_count > 0:
        print("✓ Migration completed successfully")
    else:
        print("✓ No migration needed - all files are up to date")


if __name__ == "__main__":
    main()
