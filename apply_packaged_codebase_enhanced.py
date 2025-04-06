#!/usr/bin/env python
"""
AutoQliq Codebase Application Script

This script parses a packaged codebase file with START/END markers and applies the files to the project.
It expects a specific format for each file in the packaged codebase:

################################################################################
########## START FILE: [path/to/file.ext] ##########
################################################################################
(file content)
################################################################################
########## END FILE: [path/to/file.ext] ##########
################################################################################

The script will:
1. Parse the input file to extract file paths and contents
2. Validate the data for consistency
3. Preview changes to be made
4. Apply changes after user confirmation
5. Provide detailed reporting of all operations

IMPORTANT: This script will overwrite existing files. It should only be run on a clean
Git branch created specifically for integrating AI-generated changes, to prevent
accidental loss of local work.

Usage:
    python apply_packaged_codebase_enhanced.py <packaged_codebase_file>
"""

import os
import sys
import re
import logging
import datetime
import fnmatch
from typing import Dict, List, Tuple

# Default patterns to ignore
DEFAULT_IGNORE_PATTERNS = [
    '.git/*', '.svn/*', '__pycache__/*', '*.pyc', 'build/*', 'dist/*',
    'node_modules/*', 'venv/*', '.venv/*', '*.egg-info/*'
]

# Configure logging
log_filename = f"codebase_application_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(log_filename)
    ]
)
logger = logging.getLogger(__name__)

def should_ignore_path(path: str, ignore_patterns: List[str]) -> bool:
    """
    Check if a path should be ignored based on ignore patterns.

    Args:
        path: The path to check
        ignore_patterns: List of glob patterns to ignore

    Returns:
        True if the path should be ignored, False otherwise
    """
    normalized_path = path.replace('\\', '/')
    return any(fnmatch.fnmatch(normalized_path, pattern) for pattern in ignore_patterns)

def parse_packaged_codebase(file_path: str) -> Tuple[List[str], Dict[str, str], List[Tuple[str, str]], List[str]]:
    """
    Parse the packaged codebase file and extract file paths and contents.

    Args:
        file_path: Path to the packaged codebase file

    Returns:
        Tuple containing:
            - List of file paths in order of appearance
            - Dictionary mapping file paths to content
            - List of path mismatches (start_path, end_path)
            - List of malformed blocks
    """
    logger.info(f"Starting to parse input file: {file_path}")

    # Get file size for progress reporting
    try:
        file_size = os.path.getsize(file_path)
        logger.info(f"Input file size: {file_size} bytes")
    except Exception as e:
        logger.warning(f"Could not determine file size: {e}")
        file_size = 0

    # Define the pattern to match START/END markers and file content
    # More flexible pattern to handle variations in whitespace and # symbols
    start_pattern = re.compile(
        r'#{10,}\s*' +                            # Start of marker (at least 10 #)
        r'#{5,}\s+START\s+FILE:\s+\[(.*?)\]\s+#{5,}\s*' +  # File path in START marker
        r'#{10,}\s*',                            # End of START marker
        re.DOTALL
    )

    end_pattern = re.compile(
        r'#{10,}\s*' +                            # Start of END marker
        r'#{5,}\s+END\s+FILE:\s+\[(.*?)\]\s+#{5,}\s*' +    # File path in END marker
        r'#{10,}',                                # End of END marker
        re.DOTALL
    )

    file_list = []
    file_contents = {}
    path_mismatches = []
    malformed_blocks = []

    # Process the file in chunks to avoid loading the entire file into memory
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            logger.info("Starting to process file blocks")

            # Variables to track the current file being processed
            current_file_path = None
            current_file_content = []
            in_file_content = False
            file_count = 0

            # Show progress information
            if file_size > 0:
                print(f"Parsing input file ({file_size/1024/1024:.1f} MB)...")

            # Process the file line by line
            for i, line in enumerate(f):
                # Show progress for large files
                if file_size > 0 and i % 10000 == 0:
                    position = f.tell()
                    progress_pct = min(100, position / file_size * 100)
                    print(f"Parsing progress: {progress_pct:.1f}%\r", end="")

                # Check for START marker
                start_match = start_pattern.match(line)
                if start_match and not in_file_content:
                    # Found a new file block
                    if current_file_path is not None:
                        # This shouldn't happen - we found a START without an END
                        logger.warning(f"Found START marker without matching END marker for {current_file_path}")
                        malformed_blocks.append(f"Missing END marker: {current_file_path}")

                    # Start a new file block
                    current_file_path = start_match.group(1).strip()
                    current_file_content = []
                    in_file_content = True
                    continue

                # Check for END marker
                end_match = end_pattern.match(line)
                if end_match and in_file_content:
                    # End of a file block
                    end_path = end_match.group(1).strip()

                    # Validate the file path
                    if current_file_path is None:
                        logger.warning("Found END marker without matching START marker")
                        malformed_blocks.append(f"Missing START marker for END: {end_path}")
                        continue

                    # Check for path mismatch
                    if current_file_path != end_path:
                        logger.warning(f"Mismatch between START path '{current_file_path}' and END path '{end_path}'. Using START path.")
                        path_mismatches.append((current_file_path, end_path))

                    # Check for invalid characters in path
                    if any(c in current_file_path for c in ['*', '?', '"', '<', '>', '|', ':', '\0']):
                        logger.warning(f"Path contains invalid characters: {current_file_path}")
                        malformed_blocks.append(f"Invalid path: {current_file_path}")
                        current_file_path = None
                        in_file_content = False
                        continue

                    # Check for absolute paths
                    if os.path.isabs(current_file_path):
                        logger.warning(f"Absolute paths are not allowed: {current_file_path}")
                        malformed_blocks.append(f"Absolute path: {current_file_path}")
                        current_file_path = None
                        in_file_content = False
                        continue

                    # Process the file content
                    file_content = ''.join(current_file_content)

                    # Add to file list if not already present
                    if current_file_path not in file_list:
                        file_list.append(current_file_path)
                    else:
                        logger.warning(f"Duplicate file found: {current_file_path}. Content will be overwritten with the last occurrence.")

                    # Store the content
                    content_size = len(file_content)
                    content_lines = file_content.count('\n') + 1
                    logger.info(f"Extracted content for {current_file_path}: {content_size} bytes, {content_lines} lines")
                    file_contents[current_file_path] = file_content

                    # Reset for the next file
                    current_file_path = None
                    current_file_content = []
                    in_file_content = False
                    file_count += 1

                    # Show periodic progress
                    if file_count % 10 == 0:
                        logger.info(f"Processed {file_count} files so far")

                    continue

                # If we're in a file content section, add the line to the current file content
                if in_file_content:
                    current_file_content.append(line)

            # Check if we ended with an unclosed file block
            if current_file_path is not None:
                logger.warning(f"File ended with unclosed file block: {current_file_path}")
                malformed_blocks.append(f"Unclosed file block at end of file: {current_file_path}")

            # Clear the progress line
            if file_size > 0:
                print("\nParsing complete!")

            logger.info(f"Found {len(file_list)} file blocks in the input")
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        sys.exit(1)

    # Check for any content that might have been missed due to malformed markers
    if not file_list:
        logger.error("No valid file blocks found in the input file")
        sys.exit(1)

    return file_list, file_contents, path_mismatches, malformed_blocks

def validate_parsed_data(file_list: List[str], file_contents: Dict[str, str]) -> bool:
    """
    Validate that all files in the list have corresponding content.

    Args:
        file_list: List of file paths
        file_contents: Dictionary mapping file paths to content

    Returns:
        True if valid, False otherwise
    """
    logger.info("Validating parsed data...")

    # Check for files in the list without content
    missing_files = []
    for file_path in file_list:
        if file_path not in file_contents:
            missing_files.append(file_path)

    if missing_files:
        logger.error(f"The following files are in the file list but have no content: {', '.join(missing_files)}")
        return False

    # Check for files with content but not in the list (should not happen with our parsing logic)
    extra_files = []
    for file_path in file_contents:
        if file_path not in file_list:
            extra_files.append(file_path)

    if extra_files:
        logger.warning(f"The following files have content but are not in the file list: {', '.join(extra_files)}")

    # Check for empty content
    empty_files = []
    for file_path, content in file_contents.items():
        if not content.strip():
            empty_files.append(file_path)

    if empty_files:
        logger.warning(f"The following files have empty content: {', '.join(empty_files)}")

    logger.info("Validation complete")
    return len(missing_files) == 0

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
    """Main function to run the script."""
    start_time = datetime.datetime.now()
    logger.info(f"Script started at {start_time}")

    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print(f"Usage: {sys.argv[0]} <packaged_codebase_file>")
        print("\nThis script parses a packaged codebase file with START/END markers")
        print("and applies the files to the project.")
        print("\nWARNING: This script will overwrite existing files. It should only be run")
        print("on a clean Git branch created specifically for integrating AI-generated changes.")
        sys.exit(0 if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help'] else 1)

    input_file = sys.argv[1]
    logger.info(f"Processing packaged codebase from {input_file}")

    # Parse the packaged codebase
    file_list, file_contents, path_mismatches, malformed_blocks = parse_packaged_codebase(input_file)
    logger.info(f"Found {len(file_list)} unique files in the packaged codebase")

    # Report any issues found during parsing
    if path_mismatches:
        logger.warning(f"Found {len(path_mismatches)} path mismatches")
        for start_path, end_path in path_mismatches:
            logger.warning(f"  START: {start_path} != END: {end_path}")

    if malformed_blocks:
        logger.warning(f"Found {len(malformed_blocks)} malformed blocks")
        for block in malformed_blocks:
            logger.warning(f"  {block}")

    # Validate the parsed data
    if not validate_parsed_data(file_list, file_contents):
        logger.error("Validation failed. Please check the input file format.")
        sys.exit(1)

    # Ask for confirmation
    print("\nFiles to be created or updated:")
    new_count = 0
    update_count = 0

    # Count files by status
    files_by_status = {"NEW": [], "UPDATE": []}
    for file_path in file_list:
        if should_ignore_path(file_path, DEFAULT_IGNORE_PATTERNS):
            continue

        normalized_path = os.path.normpath(file_path)
        if os.path.exists(normalized_path):
            update_count += 1
            files_by_status["UPDATE"].append(normalized_path)
        else:
            new_count += 1
            files_by_status["NEW"].append(normalized_path)

    # Display a limited number of files for each status
    max_files_to_display = 20  # Limit the number of files displayed

    if new_count > 0:
        print(f"\n  New files ({new_count} total):")
        for path in files_by_status["NEW"][:max_files_to_display]:
            print(f"    {path}")
        if new_count > max_files_to_display:
            print(f"    ... and {new_count - max_files_to_display} more")

    if update_count > 0:
        print(f"\n  Files to update ({update_count} total):")
        for path in files_by_status["UPDATE"][:max_files_to_display]:
            print(f"    {path}")
        if update_count > max_files_to_display:
            print(f"    ... and {update_count - max_files_to_display} more")

    print(f"\nSummary: {new_count} new files, {update_count} files to update")
    print("\nWARNING: This will overwrite any existing files. Make sure you are on a clean Git branch.")
    logger.info("Confirmation prompt shown to user")

    confirmation = input("\nDo you want to proceed? (y/n): ")
    if confirmation.lower() != 'y':
        logger.info("Operation cancelled by user")
        print("Operation cancelled.")
        sys.exit(0)

    logger.info("User confirmed to proceed with changes")

    # Apply the changes
    created_files, updated_files, skipped_files, failed_files = apply_changes(file_list, file_contents)

    # Calculate elapsed time
    end_time = datetime.datetime.now()
    elapsed_time = end_time - start_time

    # Print summary
    print("\nApplication completed!")
    print(f"  Created: {len(created_files)} files")
    print(f"  Updated: {len(updated_files)} files")
    print(f"  Skipped: {len(skipped_files)} files (ignored patterns)")
    print(f"  Failed: {len(failed_files)} files")
    print(f"  Total time: {elapsed_time}")

    if skipped_files:
        print("\nSkipped files (ignored patterns):")
        for file_path in skipped_files[:10]:  # Show only first 10 to avoid clutter
            print(f"  {file_path}")
        if len(skipped_files) > 10:
            print(f"  ... and {len(skipped_files) - 10} more")

    if failed_files:
        print("\nFailed files:")
        for file_path in failed_files:
            print(f"  {file_path}")

    logger.info(f"Processing complete. Created: {len(created_files)}, Overwritten: {len(updated_files)}, "
                f"Skipped: {len(skipped_files)}, Failed: {len(failed_files)}")
    logger.info(f"Script completed at {end_time} (elapsed: {elapsed_time})")

if __name__ == "__main__":
    main()
