#!/usr/bin/env python
"""
Apply changes from a file in Gemini format.

This script processes a file in the Gemini format:
1. FILE LIST section
2. Analysis section
3. FILE CONTENTS section with START/END markers

It extracts the file contents and applies them to the codebase.
"""

import os
import sys
import re
import argparse
import logging
import datetime
import fnmatch
from typing import List, Dict, Tuple

# Configure logging
log_filename = f"gemini_application_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)
logger = logging.getLogger(__name__)

# Default patterns to ignore
DEFAULT_IGNORE_PATTERNS = [
    '.git/*',
    '__pycache__/*',
    '*.pyc',
    '*.pyo',
    '*.pyd',
    '.DS_Store',
    '.vscode/*',
    '.idea/*',
    'venv/*',
    '.venv/*',
    'env/*',
    'node_modules/*',
    'dist/*',
    'build/*',
    '*.egg-info/*',
]

def is_gemini_input_file(path: str) -> bool:
    """
    Check if a file is a Gemini input file that should be preserved.

    Args:
        path: Path to check

    Returns:
        True if the file is a Gemini input file, False otherwise
    """
    # Get the base filename without path and extension
    basename = os.path.basename(path)
    basename_no_ext = os.path.splitext(basename)[0].lower()

    # Check if the filename starts with 'gemini' and is optionally followed by a number
    return basename_no_ext == 'gemini' or (basename_no_ext.startswith('gemini') and basename_no_ext[6:].isdigit())

def should_ignore_path(path: str, ignore_patterns: List[str]) -> bool:
    """
    Check if a path should be ignored based on the ignore patterns.

    Args:
        path: Path to check
        ignore_patterns: List of glob patterns to ignore

    Returns:
        True if the path should be ignored, False otherwise
    """
    # Always preserve Gemini input files
    if is_gemini_input_file(path):
        logger.info(f"Preserving Gemini input file: {path}")
        return True

    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def prepare_file_structure(
    file_list: List[str],
    ignore_patterns: List[str] = DEFAULT_IGNORE_PATTERNS
) -> Tuple[List[str], List[str]]:
    """
    Prepare the file structure by creating all necessary directories.

    Args:
        file_list: List of file paths in order of appearance
        ignore_patterns: List of glob patterns to ignore

    Returns:
        Tuple containing:
            - List of files to process
            - List of skipped files (due to ignore patterns)
    """
    logger.info("Preparing file structure...")
    files_to_process = []
    skipped_files = []
    created_dirs = set()

    for file_path in file_list:
        # Skip if the file should be ignored
        if should_ignore_path(file_path, ignore_patterns):
            logger.info(f"Skipping ignored path: {file_path}")
            skipped_files.append(file_path)
            continue

        # Normalize path separators for the current OS
        normalized_path = os.path.normpath(file_path)
        files_to_process.append(normalized_path)

        # Create directory if it doesn't exist
        directory = os.path.dirname(normalized_path)
        if directory and directory not in created_dirs and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
                created_dirs.add(directory)
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")

    logger.info(f"Prepared structure for {len(files_to_process)} files")
    return files_to_process, skipped_files

def parse_gemini_file(file_path: str) -> Tuple[List[str], Dict[str, str], List[str]]:
    """
    Parse a file in Gemini format.

    Args:
        file_path: Path to the file in Gemini format

    Returns:
        Tuple containing:
            - List of file paths in the FILE LIST section
            - Dictionary mapping file paths to content
            - List of error messages
    """
    logger.info(f"Parsing Gemini file: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        return [], {}, [f"Failed to read input file: {e}"]

    # Extract the file list
    file_list = []
    file_list_match = re.search(r'# FILE LIST\s+(.*?)(?=\s+#)', content, re.DOTALL)
    if file_list_match:
        file_list_text = file_list_match.group(1).strip()
        file_list = [line.strip() for line in file_list_text.split('\n') if line.strip() and not line.strip().startswith('Use code with caution')]
        logger.info(f"Found {len(file_list)} files in the file list")
    else:
        logger.warning("Could not find FILE LIST section")

    # Extract the file contents
    file_contents = {}
    errors = []

    # Find all START/END file blocks
    start_pattern = re.compile(
        r'#{10,}\s*' +                            # Start of marker (at least 10 #)
        r'#{5,}\s+START\s+FILE:\s+(\S+)\s+#{5,}\s*' +  # File path in START marker
        r'#{10,}\s*',                            # End of START marker
        re.DOTALL
    )

    end_pattern = re.compile(
        r'#{10,}\s*' +                            # Start of END marker
        r'#{5,}\s+END\s+FILE:\s+(\S+)\s+#{5,}\s*' +    # File path in END marker
        r'#{10,}',                                # End of END marker
        re.DOTALL
    )

    # Find all START markers
    start_matches = list(start_pattern.finditer(content))

    # Find all END markers
    end_matches = list(end_pattern.finditer(content))

    if len(start_matches) != len(end_matches):
        error_msg = f"Mismatch between START ({len(start_matches)}) and END ({len(end_matches)}) markers"
        logger.error(error_msg)
        errors.append(error_msg)

    # Process each file block
    for i, start_match in enumerate(start_matches):
        if i >= len(end_matches):
            break

        file_path = start_match.group(1).strip()
        if file_path.startswith('[') and file_path.endswith(']'):
            file_path = file_path[1:-1]  # Remove square brackets if present

        end_match = end_matches[i]
        end_file_path = end_match.group(1).strip()
        if end_file_path.startswith('[') and end_file_path.endswith(']'):
            end_file_path = end_file_path[1:-1]  # Remove square brackets if present

        # Check if START and END markers have matching file paths
        if file_path != end_file_path:
            error_msg = f"Mismatched file paths in START ({file_path}) and END ({end_file_path}) markers"
            logger.error(error_msg)
            errors.append(error_msg)
            continue

        # Extract file content
        start_pos = start_match.end()
        end_pos = end_match.start()
        file_content = content[start_pos:end_pos].strip()

        # Store the file content
        file_contents[file_path] = file_content
        logger.info(f"Extracted content for {file_path}: {len(file_content)} bytes")

    # Check if all files in the file list have content
    for file_path in file_list:
        if file_path not in file_contents:
            error_msg = f"File in list but no content found: {file_path}"
            logger.warning(error_msg)
            errors.append(error_msg)

    return file_list, file_contents, errors

def apply_changes(
    file_list: List[str],
    file_contents: Dict[str, str],
    ignore_patterns: List[str] = DEFAULT_IGNORE_PATTERNS
) -> Tuple[List[str], List[str], List[str], List[str]]:
    """
    Apply the changes to the codebase.

    Args:
        file_list: List of file paths in order of appearance
        file_contents: Dictionary mapping file paths to content
        ignore_patterns: List of glob patterns to ignore

    Returns:
        Tuple containing:
            - List of created files
            - List of updated files
            - List of skipped files (due to ignore patterns)
            - List of failed files (due to errors)
    """
    logger.info("Starting to apply changes...")
    created_files = []
    updated_files = []
    skipped_files = []
    failed_files = []

    # First, prepare the file structure by creating all necessary directories
    files_to_process, initial_skipped = prepare_file_structure(file_list, ignore_patterns)
    skipped_files.extend(initial_skipped)

    total_files = len(files_to_process)
    logger.info(f"Will process {total_files} files")

    # Display progress information
    print(f"\nApplying changes to {total_files} files...")
    progress_interval = max(1, total_files // 20)  # Show progress every 5% or at least every file

    for i, file_path in enumerate(file_list):
        # Show progress
        if i % progress_interval == 0 or i == len(file_list) - 1:
            progress_pct = (i + 1) / len(file_list) * 100
            print(f"Progress: {i + 1}/{len(file_list)} files ({progress_pct:.1f}%)\r", end="")

        # Skip if the file should be ignored
        if should_ignore_path(file_path, ignore_patterns):
            # Already counted in skipped_files from prepare_file_structure
            continue

        # Skip if no content is available (should not happen after validation)
        if file_path not in file_contents:
            logger.error(f"No content available for {file_path}")
            failed_files.append(file_path)
            continue

        content = file_contents[file_path]
        content_size = len(content)
        content_lines = content.count('\n') + 1

        # Normalize path separators for the current OS
        normalized_path = os.path.normpath(file_path)

        # Check if file exists
        file_exists = os.path.exists(normalized_path)

        # Check if this is a Gemini input file that should be preserved
        if is_gemini_input_file(normalized_path):
            logger.info(f"Skipping Gemini input file: {normalized_path}")
            skipped_files.append(normalized_path)
            continue

        # Write the file
        try:
            logger.info(f"Processing file: {normalized_path}")
            with open(normalized_path, 'w', encoding='utf-8') as f:
                f.write(content)

            if file_exists:
                logger.info(f"Overwriting file: {normalized_path} ({content_size} bytes, {content_lines} lines)")
                updated_files.append(normalized_path)
            else:
                logger.info(f"Creating file: {normalized_path} ({content_size} bytes, {content_lines} lines)")
                created_files.append(normalized_path)
        except Exception as e:
            logger.error(f"Failed to write {normalized_path}: {e}")
            failed_files.append(normalized_path)

    # Clear the progress line and move to the next line
    print("\nProcessing complete!")

    return created_files, updated_files, skipped_files, failed_files

def main():
    """Main function."""
    start_time = datetime.datetime.now()
    logger.info(f"Script started at {start_time}")

    parser = argparse.ArgumentParser(
        description='Apply changes from a file in Gemini format.'
    )
    parser.add_argument(
        'file_path',
        help='Path to the file in Gemini format'
    )
    parser.add_argument(
        '--ignore-patterns',
        nargs='+',
        default=DEFAULT_IGNORE_PATTERNS,
        help='Glob patterns to ignore (space-separated)'
    )

    args = parser.parse_args()

    # Parse the Gemini file
    logger.info(f"Processing Gemini file from {args.file_path}")
    file_list, file_contents, errors = parse_gemini_file(args.file_path)

    if not file_list:
        logger.error("No files found in the file list")
        return 1

    if not file_contents:
        logger.error("No file contents found")
        return 1

    if errors:
        logger.warning(f"Found {len(errors)} errors during parsing")
        for error in errors[:10]:  # Show only first 10 to avoid clutter
            logger.warning(f"  {error}")
        if len(errors) > 10:
            logger.warning(f"  ... and {len(errors) - 10} more")

    # Apply the changes
    created_files, updated_files, skipped_files, failed_files = apply_changes(
        file_list, file_contents, args.ignore_patterns
    )

    # Calculate elapsed time
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time

    # Print summary
    print("\nApplication complete!")
    print(f"  Created: {len(created_files)} files")
    print(f"  Updated: {len(updated_files)} files")
    print(f"  Skipped: {len(skipped_files)} files")
    print(f"  Failed: {len(failed_files)} files")
    print(f"  Total time: {elapsed_time}")

    if created_files:
        print("\nCreated files:")
        for file_path in created_files[:10]:  # Show only first 10 to avoid clutter
            print(f"  {file_path}")
        if len(created_files) > 10:
            print(f"  ... and {len(created_files) - 10} more")

    if updated_files:
        print("\nUpdated files:")
        for file_path in updated_files[:10]:  # Show only first 10 to avoid clutter
            print(f"  {file_path}")
        if len(updated_files) > 10:
            print(f"  ... and {len(updated_files) - 10} more")

    if failed_files:
        print("\nFailed files:")
        for file_path in failed_files:
            print(f"  {file_path}")

    logger.info(f"Processing complete. Created: {len(created_files)}, Updated: {len(updated_files)}, "
                f"Skipped: {len(skipped_files)}, Failed: {len(failed_files)}")
    logger.info(f"Script completed at {end_time} (elapsed: {elapsed_time})")

    return 0 if not failed_files else 1

if __name__ == "__main__":
    sys.exit(main())
