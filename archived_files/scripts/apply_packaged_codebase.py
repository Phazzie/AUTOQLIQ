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

Usage:
    python apply_packaged_codebase.py <packaged_codebase_file>
"""

import os
import sys
import re
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('codebase_application.log')
    ]
)
logger = logging.getLogger(__name__)

def parse_packaged_codebase(file_path):
    """
    Parse the packaged codebase file and extract file paths and contents.

    Args:
        file_path (str): Path to the packaged codebase file

    Returns:
        tuple: (file_list, file_contents, path_mismatches)
            file_list: List of file paths in order of appearance
            file_contents: Dictionary mapping file paths to content
            path_mismatches: List of files with mismatched START/END paths
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"Failed to read input file: {e}")
        sys.exit(1)

    # Define the pattern to match START/END markers and file content
    pattern = re.compile(
        r'#{80}\s+' +                                # Start of marker (80 #)
        r'#{10} START FILE: \[(.*?)\] #{10}\s+' +    # File path in START marker
        r'#{80}\s+' +                                # End of START marker
        r'(.*?)' +                                   # File content (non-greedy)
        r'#{80}\s+' +                                # Start of END marker
        r'#{10} END FILE: \[(.*?)\] #{10}\s+' +      # File path in END marker
        r'#{80}',                                    # End of END marker
        re.DOTALL
    )

    file_list = []
    file_contents = {}
    path_mismatches = []

    for match in pattern.finditer(content):
        start_path = match.group(1)
        file_content = match.group(2)
        end_path = match.group(3)

        # Add to file list (using start path)
        if start_path not in file_list:
            file_list.append(start_path)

        # Verify that START and END paths match
        if start_path != end_path:
            logger.warning(f"Mismatch between START path '{start_path}' and END path '{end_path}'. Using START path.")
            path_mismatches.append((start_path, end_path))

        # Check for duplicate files
        if start_path in file_contents:
            logger.warning(f"Duplicate file found: {start_path}. Using the last occurrence.")

        file_contents[start_path] = file_content

    return file_list, file_contents, path_mismatches

def apply_changes(file_contents):
    """
    Apply the changes to the codebase.

    Args:
        file_contents (dict): Dictionary mapping file paths to content

    Returns:
        tuple: (created_files, updated_files, skipped_files)
    """
    created_files = []
    updated_files = []
    skipped_files = []

    for file_path, content in file_contents.items():
        # Normalize path separators for the current OS
        normalized_path = os.path.normpath(file_path)

        # Create directory if it doesn't exist
        directory = os.path.dirname(normalized_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")

        # Check if file exists
        file_exists = os.path.exists(normalized_path)

        # Write the file
        try:
            with open(normalized_path, 'w', encoding='utf-8') as f:
                f.write(content)

            if file_exists:
                logger.info(f"Updated file: {normalized_path}")
                updated_files.append(normalized_path)
            else:
                logger.info(f"Created file: {normalized_path}")
                created_files.append(normalized_path)
        except Exception as e:
            logger.error(f"Failed to write {normalized_path}: {e}")
            skipped_files.append(normalized_path)

    return created_files, updated_files, skipped_files

def main():
    """Main function to run the script."""
    if len(sys.argv) != 2 or sys.argv[1] in ['-h', '--help']:
        print(f"Usage: {sys.argv[0]} <packaged_codebase_file>")
        print("\nThis script parses a packaged codebase file with START/END markers")
        print("and applies the files to the project.")
        sys.exit(0 if sys.argv[1] in ['-h', '--help'] else 1)

    input_file = sys.argv[1]
    logger.info(f"Processing packaged codebase from {input_file}")

    # Parse the packaged codebase
    file_contents = parse_packaged_codebase(input_file)
    logger.info(f"Found {len(file_contents)} files in the packaged codebase")

    # Ask for confirmation
    print("\nThe following files will be created or updated:")
    for file_path in sorted(file_contents.keys()):
        normalized_path = os.path.normpath(file_path)
        status = "NEW" if not os.path.exists(normalized_path) else "UPDATE"
        print(f"  [{status}] {normalized_path}")

    confirmation = input("\nDo you want to proceed? (y/n): ")
    if confirmation.lower() != 'y':
        logger.info("Operation cancelled by user")
        sys.exit(0)

    # Apply the changes
    created_files, updated_files, skipped_files = apply_changes(file_contents)

    # Print summary
    print("\nApplication completed!")
    print(f"  Created: {len(created_files)} files")
    print(f"  Updated: {len(updated_files)} files")
    print(f"  Skipped: {len(skipped_files)} files")

    if skipped_files:
        print("\nSkipped files:")
        for file_path in skipped_files:
            print(f"  {file_path}")

    logger.info("Application completed successfully")

if __name__ == "__main__":
    main()
